template <typename T>
T index(const std::vector<T>& vec, float floatIndex) {
    size_t index = static_cast<size_t>(std::round(floatIndex));

    if (index < vec.size()) {
        return vec[index];
    } else {
        throw std::out_of_range("Index out of bounds");
    }
}

template <typename T>
T index(std::vector<T>& vec, float floatIndex, const T& newValue) {
    size_t index = static_cast<size_t>(std::round(floatIndex));
    
    if (index < vec.size()) {
        T tmp = vec[index];
        vec[index] = newValue;
        return tmp;
    } else {
        throw std::out_of_range("Index out of bounds");
    }
}