import platform
import subprocess
from biro import *
from biropkg import *
import click
import tempfile
import os
import sqlite3
import yaml
from requests import Response

BIROHOME = os.environ["BIROHOME"]
BIROLIB = os.environ.get("BIROLIB", os.path.join(os.environ["BIROHOME"], "lib"))


def _make_cpp(filename):
    Preprocessor(
        filename,
        BIROLIB,
        "so.pirocode",
    ).process()
    with open("so.pirocode", "r") as f:
        code = f.read()
    os.remove("so.pirocode")
    p = Parser()
    p.parse(code)
    a = CPP(p)
    return a.make()


def _compile_cpp(file_path, output_name, making_source):
    if platform.system() == "Windows":
        if making_source:
            return
        click.echo(
            click.style(
                "Not implemented on windows yet. Use `compile -s` command",
                fg="yellow",
            )
        )
        exit(1)
    else:
        compile_command = ["g++", file_path, "-std=c++17", "-o", output_name]

    try:
        subprocess.run(compile_command, check=True)
    except subprocess.CalledProcessError as e:
        pass


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
def biro():
    """Biro - Biro language compiler/installer."""
    pass


@biro.command()
@click.argument("filename")
@click.option("-o", "--output", help="Specify an output filename")
@click.option(
    "-s",
    "--source",
    is_flag=True,
    default=False,
    help="""Generate the intermediate C++ source file.
    Use this flag to create the intermediate code file along with compiling it.""",
)
def compile(filename, output, source):
    """Compiles a biro file."""
    basename, file_ext = os.path.splitext(os.path.basename(filename))
    tempdir = os.getcwd()
    if not source:
        tempdir = tempfile.mkdtemp()
    if not os.path.exists(filename) or not os.path.isfile(filename):
        click.echo(
            f'{click.style("Error: ", bold=True, fg="red")}{click.style(f"No such file {filename} exist", fg="red")}'
        )
        exit(1)
    code = _make_cpp(filename)
    cpp_file = os.path.join(tempdir, f"{basename}.cpp")
    out_file = f"{basename}.birocode"
    if output:
        out_file = output
    with open(cpp_file, "w") as f:
        f.write(code)
    _compile_cpp(cpp_file, out_file, making_source=source)
    if not source:
        os.remove(cpp_file)
        os.rmdir(tempdir)


@biro.command()
def version():
    """Show version."""
    click.echo(__version__)


@biro.command()
def list():
    """List all commands."""
    escaped = "\n\t"
    click.echo(
        f"Available commands:{escaped}{escaped.join(biro.commands.keys())}"
    )


@biro.command()
def install():
    """Install the biro packages"""
    click.echo(
        click.style(
            "Not implemented yet.",
            fg="yellow",
        )
    )
    exit(1)


@biro.command()
def update():
    """Update the package index"""
    click.echo(
        click.style(
            "Not implemented yet.",
            fg="yellow",
        )
    )
    exit(1)

    # Make the database and tables if doesn't exists
    pre_db(BIROHOME)

    # Callback function to add change the state of index
    def insert_or_update(resp: Response, *args, **kwargs):
        try:
            if resp.status_code != 200:
                return
            yaml_data = yaml.safe_load(resp.text)
            package_name = kwargs["package_name"]
            fetch_url = kwargs["fetch_url"]
            description = yaml_data.get("description")
            readme_file_path = yaml_data.get("readme_file_path")
            version = yaml_data.get("version")
            authors = yaml_data.get("authors", "")

            con = sqlite3.connect(f"{BIROHOME}/index.db")
            with con:
                con.execute(
                    """
                    INSERT OR REPLACE INTO Packages (name, version, description, readme_file_path, fetch_url, authors)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        package_name,
                        version,
                        description,
                        readme_file_path,
                        fetch_url,
                        authors,
                    ),
                )

            con.close()
            print(f"\tIndexed {package_name}")
        except:
            pass

    with open(f"{BIROHOME}/pkg.repo", "r") as f:
        repo_list = f.readlines()

    for repo in repo_list:
        repo = repo.strip()
        loader = Loader(desc=f"Updating index => {repo}")
        loader.end = loader.desc
        loader.start()
        line = pkg_split(repo)
        if line[0] == "github":
            pkg = BiroGithub()
            if len(line) < 3:
                loader.stop()
                click.echo(
                    click.style(f"Corrupted source: {repo}", fg="yellow")
                )
                continue
            user = pkg_decode(line[1])
            _repo = pkg_decode(line[2])
            pkg.set_repo(user=user, repo=_repo)
            if len(line) >= 4:
                branch = pkg_decode(line[3])
                pkg.set_repo(user=user, repo=_repo, branch=branch)

            if len(line) == 5:
                dir = pkg_decode(line[4])
                pkg.set_repo(user=user, repo=_repo, branch=branch, dir=dir)

            pkg_list = pkg.list_pkg()
            if not pkg_list:
                loader.stop()
                click.echo(
                    click.style(f"Corrupted source: {repo}", fg="yellow")
                )
                continue
            loader.stop()

            pkg.get_metadata(pkg_list, callback=insert_or_update)


if __name__ == "__main__":
    biro(prog_name="biro")
