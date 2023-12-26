template <typename T> void printRaw(const T &value) {
    if constexpr (std::is_same_v<T, bool>) {
        std::string boolean = value ? "true" : "false";
        std::cout << boolean;
    } else {
        std::cout << value;
    }
}

template <typename T> void printVector(const std::vector<T> &vec) {
    std::cout << "[";
    for (const auto &element : vec) {
        printRaw(element);
        std::cout << ", ";
    }
    std::cout << "\b\b]";
}

template <typename T> void printQueue(const std::queue<T> &q) {
    std::queue<T> temp = q;
    std::cout << "[";
    while (!temp.empty()) {
        printRaw(temp.front());
        std::cout << ", ";
        temp.pop();
    }
    std::cout << "\b\b]";
}

template <typename T> void printStack(const std::stack<T> &s) {
    std::stack<T> temp = s;
    std::cout << "[";
    while (!temp.empty()) {
        printRaw(temp.top());
        std::cout << ", ";
        temp.pop();
    }
    std::cout << "\b\b]";
}

template <typename T> void say(const T &value) {
    if constexpr (std::is_same_v<T, float> || std::is_same_v<T, std::string> ||
                std::is_same_v<T, bool>) {
        printRaw(value);
    } else if constexpr (std::is_same_v<T,
                                        std::vector<typename T::value_type>>) {
        printVector(value);
    } else if constexpr (std::is_same_v<T,
                                        std::queue<typename T::value_type>>) {
        printQueue(value);
    } else if constexpr (std::is_same_v<T,
                                        std::stack<typename T::value_type>>) {
        printStack(value);
    }
}

template <typename T, typename... Args>
void say(const T &value, const Args &...args) {
    if constexpr (std::is_same_v<T, float> || std::is_same_v<T, std::string> ||
                std::is_same_v<T, bool>) {
        printRaw(value);
    } else if constexpr (std::is_same_v<T,
                                        std::vector<typename T::value_type>>) {
        printVector(value);
    } else if constexpr (std::is_same_v<T,
                                        std::queue<typename T::value_type>>) {
        printQueue(value);
    } else if constexpr (std::is_same_v<T,
                                        std::stack<typename T::value_type>>) {
        printStack(value);
    }

    say(args...);
}