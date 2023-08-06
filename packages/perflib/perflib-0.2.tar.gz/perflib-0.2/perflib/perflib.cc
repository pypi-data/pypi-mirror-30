#include <Python.h>

#include "libperf.hh"

extern "C" {

    typedef struct {

        PyObject_HEAD
        libperf::PerfCounter *counter;

    } PerfCounter;

    static PyObject*
    PerfCounter_new(PyTypeObject *type, PyObject *, PyObject *) {

        PerfCounter *self;

        self = (PerfCounter*)type->tp_alloc(type, 0);
        if(self == NULL) {
            PyErr_SetString(PyExc_ValueError, "Could not alloc a new PerfCounter.");
            return 0;
        }

        return (PyObject*) self;
    }

    static void
    PerfCounter_dealloc(PerfCounter* self) {

        delete self->counter;
        Py_TYPE(self)->tp_free((PyObject*)self);
    }
    
    static int
    PerfCounter_init(PerfCounter *self, PyObject *args, PyObject *kwargs) {

        char *counter_name = NULL;

        static char *kwlist[] = { "counter_name", NULL };
        if (!PyArg_ParseTupleAndKeywords(args,
                                         kwargs,
                                         "s",
                                         kwlist,
                                         &counter_name)){

            PyErr_SetString(PyExc_ValueError, "PerfCounter failed while parsing constructor args/kwargs.");
            return 0;
        }

        if(counter_name == NULL) {

            PyErr_SetString(PyExc_ValueError, "PerfCounter requires `counter_name` to be specified.");
            return 0;
        }

        // std::cerr << "got it: '" << counter_name << "'\n";
        try {

            libperf::PerfCounter *p = new libperf::PerfCounter{std::string(counter_name)};
            self->counter = p;
        }
        catch(const std::exception& e) {

            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }
        
        return 0;
    }

    static PyObject*
    PerfCounter_start(PerfCounter *self){

        try {
            self->counter->start();
        }
        catch(const std::exception& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }        

        Py_RETURN_NONE;
    }

    static PyObject*
    PerfCounter_stop(PerfCounter *self){

        try {
            self->counter->stop();
        }
        catch(const std::exception& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }

        Py_RETURN_NONE;
    }

    static PyObject*
    PerfCounter_reset(PerfCounter *self){

        try {
            self->counter->reset();       
        }
        catch(const std::exception& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }

        Py_RETURN_NONE;
    }

    static PyObject*
    PerfCounter_getval(PerfCounter *self){

        uint64_t counter_val;
        try {
            counter_val = self->counter->getval();
        }
        catch(const std::exception& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }

        static_assert(sizeof(uint64_t) <= sizeof(unsigned long long), "sizeof(uint64_t) <= sizeof(long long) must be true");
        PyObject *val = PyLong_FromUnsignedLongLong(static_cast<unsigned long long>(counter_val));
        
        return val;
    }

    static PyMethodDef PerfCounter_methods[] = {
        {"start", (PyCFunction)PerfCounter_start, METH_VARARGS,
              "Returns labels for objects in the frame by pushing the frame through the YOLO CNN."
        },
        {"stop", (PyCFunction)PerfCounter_stop, METH_VARARGS,
              "Returns labels for objects in the frame by pushing the frame through the YOLO CNN."
        },
        {"reset", (PyCFunction)PerfCounter_reset, METH_VARARGS,
              "Returns labels for objects in the frame by pushing the frame through the YOLO CNN."
        },
        {"getval", (PyCFunction)PerfCounter_getval, METH_VARARGS,
              "Returns labels for objects in the frame by pushing the frame through the YOLO CNN."
        },
        {NULL, NULL, METH_VARARGS, ""}  /* Sentinel */
    };
    
    static PyTypeObject PerfCounterType = {
        PyObject_HEAD_INIT(NULL)
        .tp_name = "perflib.PerfCounter",
        .tp_basicsize = sizeof(PerfCounter),
        .tp_itemsize = 0,
        .tp_dealloc = (destructor)PerfCounter_dealloc,
        .tp_print = 0,
        .tp_getattr = 0,
        .tp_setattr = 0,
        .tp_as_async = 0,
        .tp_repr = 0,
        .tp_as_number = 0,
        .tp_as_sequence = 0,
        .tp_as_mapping = 0,
        .tp_hash = 0,
        .tp_call = 0,
        .tp_str = 0,
        .tp_getattro = 0,
        .tp_setattro = 0,
        .tp_as_buffer = 0,
        .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
        .tp_doc = "PerfCounter object",
        .tp_traverse = 0,
        .tp_clear = 0,
        .tp_richcompare = 0,
        .tp_weaklistoffset = 0,
        .tp_iter = 0,
        .tp_iternext = 0,
        .tp_methods = PerfCounter_methods,
        .tp_members = 0,
        .tp_getset = 0,
        .tp_base = 0,
        .tp_dict = 0,
        .tp_descr_get = 0,
        .tp_descr_set = 0,
        .tp_dictoffset = 0,
        .tp_init = (initproc)PerfCounter_init,
        .tp_alloc = 0,
        .tp_new = PerfCounter_new,
        .tp_free = 0,
        .tp_is_gc = 0,
        .tp_bases = 0,
        .tp_mro = 0,
        .tp_cache = 0,
        .tp_subclasses = 0,
        .tp_weaklist = 0,
        .tp_del = 0,
        .tp_version_tag = 0,
        .tp_finalize = 0,
    };

    struct module_state {
        PyObject *error;
    };

    static PyObject* perflib_get_available_counters(void) {

        std::vector<std::string> available_counters;
        size_t num_counters;
        try {
            available_counters = libperf::get_counters_available();
            num_counters = available_counters.size();
        }
        catch(const std::exception& e) {
            PyErr_SetString(PyExc_ValueError, e.what());
            return 0;
        }

        static_assert(sizeof(Py_ssize_t) >= sizeof(size_t), "sizeof(Py_ssize_t) >= sizeof(size_t) must be true.");
        PyObject* available_counters_list = PyList_New(static_cast<Py_ssize_t>(num_counters));
        if(available_counters_list == NULL){
            PyErr_SetString(PyExc_ValueError, "could not create a new python list to put the available counters into.");
            return 0;
        }

        for(size_t i = 0; i < num_counters; i++) {

            PyObject* counter_name = PyUnicode_FromString(available_counters[i].c_str());
            if(counter_name == NULL){
                PyErr_SetString(PyExc_ValueError, "could not insert counter_name string into python list.");
                return 0;
            }
            PyList_SET_ITEM(available_counters_list, i, counter_name);

        }
        
        return available_counters_list;
    }
    
    static PyMethodDef module_methods[] = {
        { "get_available_counters", (PyCFunction)perflib_get_available_counters, METH_NOARGS, NULL },
        {NULL, NULL, 0, NULL}  /* Sentinel */
    };
    
    static struct PyModuleDef module_def = {
        PyModuleDef_HEAD_INIT,
        .m_name = "perflib",
        .m_doc = "a python library for accessing CPU performance counters on linux.",
        .m_size = sizeof(struct module_state),
        .m_methods = module_methods,
        .m_slots = 0,
        .m_traverse = 0,
        .m_clear = 0,
        .m_free = 0
    };
    
    PyMODINIT_FUNC
    PyInit_perflib(void)
    {

        if (PyType_Ready(&PerfCounterType) < 0){
            PyErr_SetString(PyExc_ValueError, "could not intialize PerfCounter object.");
            return 0;
        }

        PyObject* module = PyModule_Create(&module_def);

        if (module == NULL){
            PyErr_SetString(PyExc_ValueError, "could not create perlib module.");
            return 0;
        }

        Py_INCREF(&PerfCounterType);
        PyModule_AddObject(module, "PerfCounter", (PyObject *)&PerfCounterType);

        PyObject *module_namespace = PyModule_GetDict(module);
        PyObject *version = PyUnicode_FromString(libperf::version_);

        if(PyDict_SetItemString(module_namespace, "__version__", version)){
            PyErr_SetString(PyExc_ValueError, "could not set __version__ of perflib module.");
            return 0;
        }

        return module;
    }

}
