import glob
import json
import os
import re
from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration, ConanException


class ConanRecipe(ConanFile):
    name = "optick"

    description = "C++ Profiler For Games "
    topics = ("c-plus-plus", "profiler", "games", "performance")

    homepage = "https://github.com/bombomby/optick"
    url = "https://github.com/conan-io/conan-center-index"

    license = "MIT License"

    exports_sources = ["CMakeLists.txt", "patches/**"]
    generators = "cmake"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "fPIC": [True, False],
        "d3d12": [True, False],
        "vulkan": [True, False],
    }
    default_options = {
        "fPIC": True,
        "d3d12": False,
        "vulkan": False,
    }

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"
    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
        else:
            del self.options.d3d12

    def configure(self):
        if self.settings.compiler.cppstd:
            tools.check_min_cppstd(self, 11)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = glob.glob('optick-*/')[0]
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        for patch in self.conan_data.get("patches", {}).get(self.version, []):
            tools.patch(**patch)
        cmake = self._configure_cmake()
        cmake.build()

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake
        self._cmake = CMake(self)
        self._cmake.definitions["OPTICK_USE_D3D12"] = self.options.d3d12
        self._cmake.definitions["OPTICK_USE_VULKAN"] = self.options.vulkan
        self._cmake.configure(build_folder=self._build_subfolder)
        return self._cmake


    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy("optick.config.h", dst="include/Optick", src=self._source_subfolder + "/src")
        self.copy("optick.h", dst="include/Optick", src=self._source_subfolder + "/src")
        self.copy("*.dll", dst="bin", src=self._build_subfolder + "/bin")
        self.copy("*.lib", dst="lib", src=self._build_subfolder + "/lib")

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "optick"
        self.cpp_info.names["cmake_find_package_multi"] = "optick"
        self.cpp_info.libs = tools.collect_libs(self)
