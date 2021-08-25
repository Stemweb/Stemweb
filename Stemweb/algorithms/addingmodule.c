#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <assert.h>
#include <math.h>
#include <sys/time.h>
#include <sys/types.h>
#include <dirent.h>
#include <zlib.h>


static PyObject* method_add(PyObject* self, PyObject* args)
{
    printf("'%s'\n", "adding 2 integers +++++++++++++++++++++++++++++++++++");
    int x,y,res = -1;
    if (!PyArg_ParseTuple(args, "ii", &x, &y))
        return NULL;
    res = x + y;
    return PyLong_FromLong(res);	
}

// Method definition object for this extension
static PyMethodDef adding_methods[] = {       
  //{"add", (PyCFunction)method_add, METH_VARARGS, "execute adding function"},
  {"add", method_add, METH_VARARGS, "execute adding function"},
        /* "add": the name the user would write to invoke this particular function
            method_add: the name of the C function to invoke
            METH_VARARGS is a flag that tells the interpreter that the function will accept two arguments of type PyObject*:
                    self is the module object.
                    args is a tuple containing the actual arguments to your function
            The final string is a value to represent the method docstring
        */    
  {NULL, NULL, 0, NULL}   /* Sentinel */
  /* https://stackoverflow.com/questions/30359255/python-sentinel-in-c-extension
     https://stackoverflow.com/questions/43371780/why-does-pymethoddef-arrays-require-a-sentinel-element-containing-multiple-nulls   */
};

// Module definition
// The arguments of this structure tell Python what to call the extension,
// what it's methods are and where to look for it's method definitions
static struct PyModuleDef addingmod =
{
    PyModuleDef_HEAD_INIT,  /*  is a member of type PyModuleDef_Base, which is advised to have just this one value. */
    "adding", /* the name of your Python C extension module */
    "a Python module that adds 2 integers via C code extension.", /* represents your module docstring; module documentation, may be NULL */
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. 
        Detailed:
        the amount of memory needed to store your program state. It’s helpful when your module is used in multiple sub-interpreters, 
        and it can have the following values:
            A negative value indicates that this module doesn’t have support for sub-interpreters.
            A non-negative value enables the re-initialization of your module. It also specifies the memory requirement of 
                your module to be allocated on each sub-interpreter session    
        */

    adding_methods  /*  is the reference to your method table. This is the array of PyMethodDef structs you defined earlier */
};

// Module initialization function
// Python calls this function when importing your extension. It is important
// that this function is named PyInit_[[your_module_name]] exactly, and matches
// the name keyword argument in setup.py's setup() call.


//static PyObject *addingError;

PyMODINIT_FUNC PyInit_adding(void)
{
    /*
    PyObject *m;

    m = PyModule_Create(&adding);
    if (m == NULL)
        return NULL;
    
    addingError = PyErr_NewException("adding.error", NULL, NULL);
    Py_XINCREF(addingError);
    if (PyModule_AddObject(m, "error", addingError) < 0) {
        Py_XDECREF(addingError);
        Py_CLEAR(addingError);
        Py_DECREF(m);
        return NULL;
    }
     
    return m;
    */

    //Py_Initialize();
    return PyModule_Create(&addingmod);
}