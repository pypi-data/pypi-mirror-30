#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <numpy/arrayobject.h>

typedef double tfloat;

static PyObject *_ctreeshap_tree_shap(PyObject *self, PyObject *args);

static PyMethodDef module_methods[] = {
  {"tree_shap", _ctreeshap_tree_shap, METH_VARARGS, "C implementation of Tree SHAP."},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC PyInit__ctreeshap(void)
{
  PyObject *module;
  static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_ctreeshap",
    "This module provides an interface for a fast Tree SHAP implementation.",
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL
  };
  module = PyModule_Create(&moduledef);
  if (!module) return NULL;

  /* Load `numpy` functionality. */
  import_array();

  return module;
}


static PyObject *_ctreeshap_tree_shap(PyObject *self, PyObject *args)
{

  PyObject *children_left_obj;
  PyObject *children_right_obj;
  PyObject *children_default_obj;
  PyObject *features_obj;
  PyObject *thresholds_obj;
  PyObject *values_obj;
  PyObject *node_sample_weight_obj;
  PyObject *x_obj;
  PyObject *x_missing_obj;
  PyObject *out_contribs_obj;
  int condition;
  int condition_feature;

  /* Parse the input tuple */
  if (!PyArg_ParseTuple(
    args, "OOOOOOOOOOii", &children_left_obj, &children_right_obj, &children_default_obj,
    &features_obj, &thresholds_obj, &values_obj, &node_sample_weight_obj, &x_obj,
    &x_missing_obj, &out_contribs_obj, &condition, &condition_feature
  )) return NULL;

  /* Interpret the input objects as numpy arrays. */
  PyObject *children_left_array = PyArray_FROM_OTF(children_left_obj, NPY_INT, NPY_ARRAY_IN_ARRAY);
  PyObject *children_right_array = PyArray_FROM_OTF(children_right_obj, NPY_INT, NPY_ARRAY_IN_ARRAY);
  PyObject *children_default_array = PyArray_FROM_OTF(children_default_obj, NPY_INT, NPY_ARRAY_IN_ARRAY);
  PyObject *features_array = PyArray_FROM_OTF(features_obj, NPY_INT, NPY_ARRAY_IN_ARRAY);
  PyObject *thresholds_array = PyArray_FROM_OTF(thresholds_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
  PyObject *values_array = PyArray_FROM_OTF(values_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
  PyObject *node_sample_weight_array = PyArray_FROM_OTF(node_sample_weight_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
  PyObject *x_array = PyArray_FROM_OTF(x_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);
  PyObject *x_missing_array = PyArray_FROM_OTF(x_missing_obj, NPY_BOOL, NPY_ARRAY_IN_ARRAY);
  PyObject *out_contribs_array = PyArray_FROM_OTF(out_contribs_obj, NPY_DOUBLE, NPY_ARRAY_IN_ARRAY);

  /* If that didn't work, throw an exception. */
  if (children_left_array == NULL || children_right_array == NULL ||
      children_default_array == NULL || features_array == NULL || thresholds_array == NULL ||
      values_array == NULL || node_sample_weight_array == NULL || x_array == NULL ||
      x_missing_array == NULL || out_contribs_array == NULL) {
    Py_XDECREF(children_left_array);
    Py_XDECREF(children_right_array);
    Py_XDECREF(children_default_array);
    Py_XDECREF(features_array);
    Py_XDECREF(thresholds_array);
    Py_XDECREF(values_array);
    Py_XDECREF(node_sample_weight_array);
    Py_XDECREF(x_array);
    Py_XDECREF(x_missing_array);
    Py_XDECREF(out_contribs_array);
    return NULL;
  }

  /* How many data points are there? */
  const unsigned M = (int)PyArray_DIM(x_array, 0);

  /* Get pointers to the data as C-types. */
  int *children_left = (int*)PyArray_DATA(children_left_array);
  int *children_right = (int*)PyArray_DATA(children_right_array);
  int *children_default = (int*)PyArray_DATA(children_default_array);
  int *features_right = (int*)PyArray_DATA(features_array);
  tfloat *thresholds_right = (tfloat*)PyArray_DATA(thresholds_array);
  tfloat *values = (tfloat*)PyArray_DATA(values_array);
  tfloat *node_sample_weight = (tfloat*)PyArray_DATA(node_sample_weight_array);
  tfloat *x = (tfloat*)PyArray_DATA(x_array);
  bool *x_missing = (bool*)PyArray_DATA(x_missing_array);
  tfloat *out_contribs = (tfloat*)PyArray_DATA(out_contribs_array);

  const int max_depth = compute_expectations(children_left, children_right,
                                             node_sample_weight, values, 0, 0);

  calculate_contributions(M, max_depth, children_left, children_right, children_default, features,
                          thresholds, values, node_sample_weight, x, x_missing, out_contribs,
                          condition, condition_feature);

  Py_XDECREF(children_left_array);
  Py_XDECREF(children_right_array);
  Py_XDECREF(children_default_array);
  Py_XDECREF(features_array);
  Py_XDECREF(thresholds_array);
  Py_XDECREF(values_array);
  Py_XDECREF(node_sample_weight_array);
  Py_XDECREF(x_array);
  Py_XDECREF(x_missing_array);
  Py_XDECREF(out_contribs_array);

                                      // unsigned M
                                      // unsigned max_depth
  // double m, b;
  // PyObject *x_obj, *y_obj, *yerr_obj;
  //
  // /* Parse the input tuple */
  // if (!PyArg_ParseTuple(args, "ddOOO", &m, &b, &x_obj, &y_obj,
  //                                     &yerr_obj))
  //     return NULL;
  //
  // /* Interpret the input objects as numpy arrays. */
  // PyObject *x_array = PyArray_FROM_OTF(x_obj, NPY_DOUBLE, NPY_IN_ARRAY);
  // PyObject *y_array = PyArray_FROM_OTF(y_obj, NPY_DOUBLE, NPY_IN_ARRAY);
  // PyObject *yerr_array = PyArray_FROM_OTF(yerr_obj, NPY_DOUBLE,
  //                                         NPY_IN_ARRAY);
  //
  // /* If that didn't work, throw an exception. */
  // if (x_array == NULL || y_array == NULL || yerr_array == NULL) {
  //     Py_XDECREF(x_array);
  //     Py_XDECREF(y_array);
  //     Py_XDECREF(yerr_array);
  //     return NULL;
  // }
  //
  // /* How many data points are there? */
  // int N = (int)PyArray_DIM(x_array, 0);
  //
  // /* Get pointers to the data as C-types. */
  // double *x    = (double*)PyArray_DATA(x_array);
  // double *y    = (double*)PyArray_DATA(y_array);
  // double *yerr = (double*)PyArray_DATA(yerr_array);
  //
  // /* Call the external C function to compute the chi-squared. */
  // double value = chi2(m, b, x, y, yerr, N);
  //
  // /* Clean up. */
  // Py_DECREF(x_array);
  // Py_DECREF(y_array);
  // Py_DECREF(yerr_array);
  //
  // if (value < 0.0) {
  //     PyErr_SetString(PyExc_RuntimeError,
  //                 "Chi-squared returned an impossible value.");
  //     return NULL;
  // }

  // const int max_depth = compute_expectations(children_left, children_right, node_sample_weight, values, 0, 0);
  //
  // calculate_contributions(const unsigned M, const unsigned max_depth, const int *children_left,
  //                                     const int *children_right,
  //                                     const int *children_default, const int *features,
  //                                     const tfloat *thresholds, const tfloat *values,
  //                                     const tfloat *node_sample_weight,
  //                                     const tfloat *x, const bool *x_missing, unsigned root_id,
  //                                     tfloat *out_contribs, int condition,
  //                                     unsigned condition_feature) const {
    // find the expected value of the tree's predictions
    //const int max_depth = compute_expectations(children_left, children_right, node_sample_weight, values, i, depth=0);


  /* Build the output tuple */
  PyObject *ret = Py_BuildValue("d", 3.4);
  return ret;
}

// data we keep about our decision path
// note that pweight is included for convenience and is not tied with the other attributes
// the pweight of the i'th path element is the permuation weight of paths with i-1 ones in them
struct PathElement {
  int feature_index;
  bst_float zero_fraction;
  bst_float one_fraction;
  bst_float pweight;
  PathElement() {}
  PathElement(int i, bst_float z, bst_float o, bst_float w) :
    feature_index(i), zero_fraction(z), one_fraction(o), pweight(w) {}
};

// extend our decision path with a fraction of one and zero extensions
inline void extend_path(PathElement *unique_path, unsigned unique_depth,
                        bst_float zero_fraction, bst_float one_fraction, int feature_index) {
  unique_path[unique_depth].feature_index = feature_index;
  unique_path[unique_depth].zero_fraction = zero_fraction;
  unique_path[unique_depth].one_fraction = one_fraction;
  unique_path[unique_depth].pweight = (unique_depth == 0 ? 1.0f : 0.0f);
  for (int i = unique_depth - 1; i >= 0; i--) {
    unique_path[i + 1].pweight += one_fraction * unique_path[i].pweight * (i + 1)
                                  / static_cast<bst_float>(unique_depth + 1);
    unique_path[i].pweight = zero_fraction * unique_path[i].pweight * (unique_depth - i)
                             / static_cast<bst_float>(unique_depth + 1);
  }
}

// undo a previous extension of the decision path
inline void unwind_path(PathElement *unique_path, unsigned unique_depth, unsigned path_index) {
  const bst_float one_fraction = unique_path[path_index].one_fraction;
  const bst_float zero_fraction = unique_path[path_index].zero_fraction;
  bst_float next_one_portion = unique_path[unique_depth].pweight;

  for (int i = unique_depth - 1; i >= 0; --i) {
    if (one_fraction != 0) {
      const bst_float tmp = unique_path[i].pweight;
      unique_path[i].pweight = next_one_portion * (unique_depth + 1)
                               / static_cast<bst_float>((i + 1) * one_fraction);
      next_one_portion = tmp - unique_path[i].pweight * zero_fraction * (unique_depth - i)
                               / static_cast<bst_float>(unique_depth + 1);
    } else {
      unique_path[i].pweight = (unique_path[i].pweight * (unique_depth + 1))
                               / static_cast<bst_float>(zero_fraction * (unique_depth - i));
    }
  }

  for (auto i = path_index; i < unique_depth; ++i) {
    unique_path[i].feature_index = unique_path[i+1].feature_index;
    unique_path[i].zero_fraction = unique_path[i+1].zero_fraction;
    unique_path[i].one_fraction = unique_path[i+1].one_fraction;
  }
}

// determine what the total permuation weight would be if
// we unwound a previous extension in the decision path
inline bst_float unwound_path_sum(const PathElement *unique_path, unsigned unique_depth,
                                  unsigned path_index) {
  const bst_float one_fraction = unique_path[path_index].one_fraction;
  const bst_float zero_fraction = unique_path[path_index].zero_fraction;
  bst_float next_one_portion = unique_path[unique_depth].pweight;
  bst_float total = 0;
  for (int i = unique_depth - 1; i >= 0; --i) {
    if (one_fraction != 0) {
      const bst_float tmp = next_one_portion * (unique_depth + 1)
                            / static_cast<bst_float>((i + 1) * one_fraction);
      total += tmp;
      next_one_portion = unique_path[i].pweight - tmp * zero_fraction * ((unique_depth - i)
                         / static_cast<bst_float>(unique_depth + 1));
    } else {
      total += (unique_path[i].pweight / zero_fraction) / ((unique_depth - i)
               / static_cast<bst_float>(unique_depth + 1));
    }
  }
  return total;
}

// recursive computation of SHAP values for a decision tree
inline void tree_shap_recursive(const int *children_left, const int *children_right,
                                const int *children_default, const int *features,
                                const tfloat *thresholds, const tfloat *values,
                                const tfloat *node_sample_weight,
                                const tfloat *x, const bool *x_missing, tfloat *phi,
                                unsigned node_index, unsigned unique_depth,
                                PathElement *parent_unique_path, tfloat parent_zero_fraction,
                                tfloat parent_one_fraction, int parent_feature_index,
                                int condition, unsigned condition_feature,
                                tfloat condition_fraction) const {

  // stop if we have no weight coming down to us
  if (condition_fraction == 0) return;

  // extend the unique path
  PathElement *unique_path = parent_unique_path + unique_depth + 1;
  std::copy(parent_unique_path, parent_unique_path + unique_depth + 1, unique_path);

  if (condition == 0 || condition_feature != static_cast<unsigned>(parent_feature_index)) {
    extend_path(unique_path, unique_depth, parent_zero_fraction,
               parent_one_fraction, parent_feature_index);
  }
  const unsigned split_index = features[node_index];

  // leaf node
  if (children_right[node_index] == -1) {
    for (unsigned i = 1; i <= unique_depth; ++i) {
      const tfloat w = unwound_path_sum(unique_path, unique_depth, i);
      const PathElement &el = unique_path[i];
      phi[el.feature_index] += w * (el.one_fraction - el.zero_fraction)
                                 * values[node_index] * condition_fraction;
    }

  // internal node
  } else {
    // find which branch is "hot" (meaning x would follow it)
    unsigned hot_index = 0;
    if (x_missing[split_index]) {
      hot_index = children_default[node_index];
    } else if (feat.fvalue(split_index) < node.split_cond()) {
      hot_index = children_left[node_index];
    } else {
      hot_index = children_right[node_index];
    }
    const unsigned cold_index = (static_cast<int>(hot_index) == children_left[node_index] ?
                                 children_right[node_index] : children_left[node_index]);
    const tfloat w = node_sample_weight[node_index];
    const tfloat hot_zero_fraction = node_sample_weight[hot_index] / w;
    const tfloat cold_zero_fraction = node_sample_weight[cold_index] / w;
    tfloat incoming_zero_fraction = 1;
    tfloat incoming_one_fraction = 1;

    // see if we have already split on this feature,
    // if so we undo that split so we can redo it for this node
    unsigned path_index = 0;
    for (; path_index <= unique_depth; ++path_index) {
      if (static_cast<unsigned>(unique_path[path_index].feature_index) == split_index) break;
    }
    if (path_index != unique_depth + 1) {
      incoming_zero_fraction = unique_path[path_index].zero_fraction;
      incoming_one_fraction = unique_path[path_index].one_fraction;
      unwind_path(unique_path, unique_depth, path_index);
      unique_depth -= 1;
    }

    // divide up the condition_fraction among the recursive calls
    tfloat hot_condition_fraction = condition_fraction;
    tfloat cold_condition_fraction = condition_fraction;
    if (condition > 0 && split_index == condition_feature) {
      cold_condition_fraction = 0;
      unique_depth -= 1;
    } else if (condition < 0 && split_index == condition_feature) {
      hot_condition_fraction *= hot_zero_fraction;
      cold_condition_fraction *= cold_zero_fraction;
      unique_depth -= 1;
    }

    tree_shap(
      children_left, children_right, children_default, features, thresholds, values,
      node_sample_weight, x, x_missing, phi, hot_index, unique_depth + 1, unique_path,
      hot_zero_fraction * incoming_zero_fraction, incoming_one_fraction,
      split_index, condition, condition_feature, hot_condition_fraction
    );

    tree_shap(
      children_left, children_right, children_default, features, thresholds, values,
      node_sample_weight, x, x_missing, phi, cold_index, unique_depth + 1, unique_path,
      cold_zero_fraction * incoming_zero_fraction, 0,
      split_index, condition, condition_feature, cold_condition_fraction
    );
  }
}

inline int compute_expectations(const int *children_left, const int *children_right,
                                const tfloat *node_sample_weight, const tfloat *values,
                                int i, int depth) {
    if (children_right[i] == -1) {
      return 0;
    } else {
      li = children_left[i]
      ri = children_right[i]
      depth_left = compute_expectations(children_left, children_right, node_sample_weight, values, li, depth + 1)
      depth_right = compute_expectations(children_left, children_right, node_sample_weight, values, ri, depth + 1)
      left_weight = node_sample_weight[li]
      right_weight = node_sample_weight[ri]
      v = (left_weight * values[li] + right_weight * values[ri]) / (left_weight + right_weight)
      values[i] = v
      return std::max(depth_left, depth_right) + 1
    }
}

inline void calculate_contributions(const unsigned M, const unsigned max_depth, const int *children_left,
                                    const int *children_right,
                                    const int *children_default, const int *features,
                                    const tfloat *thresholds, const tfloat *values,
                                    const tfloat *node_sample_weight,
                                    const tfloat *x, const bool *x_missing,
                                    tfloat *out_contribs, int condition,
                                    unsigned condition_feature) const {
  // find the expected value of the tree's predictions
  //const int max_depth = compute_expectations(children_left, children_right, node_sample_weight, values, i, depth=0);
  if (condition == 0) {
    out_contribs[M - 1] += values[0];
  }

  // Preallocate space for the unique path data
  //const int maxd = this->MaxDepth(root_id) + 2;
  PathElement *unique_path_data = new PathElement[(max_depth * (max_depth + 1)) / 2];

  tree_shap(
    children_left, children_right, children_default, features, thresholds, values,
    node_sample_weight, x, x_missing, out_contribs, root_id, 0, unique_path_data,
    1, 1, -1, condition, condition_feature, 1
  );
  delete[] unique_path_data;
}
