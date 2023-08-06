#include <functional>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

#include <ROL_PartitionedVector.hpp>

void init_partitionedvector(py::module& m) {
  py::class_<ROL::PartitionedVector<double>,
             std::shared_ptr<ROL::PartitionedVector<double>>>(m, "PartitionedVector")
      .def(py::init<>());
}
