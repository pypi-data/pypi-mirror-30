from cffi import FFI


_FFI = FFI()
_FFI.set_source('ssc._ffi', None)
_FFI.cdef('''
// Manually exported from sscapi.h

// API constants
#define SSC_INVALID 0
#define SSC_STRING 1
#define SSC_NUMBER 2
#define SSC_ARRAY 3
#define SSC_MATRIX 4
#define SSC_TABLE 5
#define SSC_INPUT 1
#define SSC_OUTPUT 2
#define SSC_INOUT 3
#define SSC_LOG 0
#define SSC_UPDATE 1
#define SSC_NOTICE 1
#define SSC_WARNING 2
#define SSC_ERROR 3

// API functions
int ssc_version();

const char *ssc_build_info();

typedef void* ssc_data_t;

typedef float ssc_number_t;

typedef int ssc_bool_t;

ssc_data_t ssc_data_create();

void ssc_data_free(ssc_data_t p_data);

void ssc_data_clear(ssc_data_t p_data);

void ssc_data_unassign(ssc_data_t p_data, const char *name);

int ssc_data_rename(ssc_data_t p_data, const char *oldname, const char *newname);

int ssc_data_query(ssc_data_t p_data, const char *name);

const char *ssc_data_first(ssc_data_t p_data);

const char *ssc_data_next(ssc_data_t p_data);

void ssc_data_set_string(ssc_data_t p_data, const char *name, const char *value);

void ssc_data_set_number(ssc_data_t p_data, const char *name, ssc_number_t value);

void ssc_data_set_array(ssc_data_t p_data, const char *name, ssc_number_t *pvalues, int length);

void ssc_data_set_matrix(ssc_data_t p_data, const char *name, ssc_number_t *pvalues, int nrows,
                         int ncols);

void ssc_data_set_table(ssc_data_t p_data, const char *name, ssc_data_t table);

const char *ssc_data_get_string(ssc_data_t p_data, const char *name);

ssc_bool_t ssc_data_get_number(ssc_data_t p_data, const char *name, ssc_number_t *value);

ssc_number_t *ssc_data_get_array(ssc_data_t p_data, const char *name, int *length);

ssc_number_t *ssc_data_get_matrix(ssc_data_t p_data, const char *name, int *nrows, int *ncols);

ssc_data_t ssc_data_get_table(ssc_data_t p_data, const char *name);

typedef void* ssc_entry_t;

ssc_entry_t ssc_module_entry(int index);

const char *ssc_entry_name(ssc_entry_t p_entry);

const char *ssc_entry_description(ssc_entry_t p_entry);

int ssc_entry_version(ssc_entry_t p_entry);

typedef void* ssc_module_t;

typedef void* ssc_info_t;

ssc_module_t ssc_module_create(const char *name);

void ssc_module_free(ssc_module_t p_mod);

const ssc_info_t ssc_module_var_info(ssc_module_t p_mod, int index);

int ssc_info_var_type(ssc_info_t p_inf);

int ssc_info_data_type(ssc_info_t p_inf);

const char *ssc_info_name(ssc_info_t p_inf);

const char *ssc_info_label(ssc_info_t p_inf);

const char *ssc_info_units(ssc_info_t p_inf);

const char *ssc_info_meta(ssc_info_t p_inf);

const char *ssc_info_group(ssc_info_t p_inf);

const char *ssc_info_required(ssc_info_t p_inf);

const char *ssc_info_constraints(ssc_info_t p_inf);

const char *ssc_info_uihint(ssc_info_t p_inf);

void ssc_module_exec_set_print(int print);

ssc_bool_t ssc_module_exec_simple(const char *name, ssc_data_t p_data);

const char *ssc_module_exec_simple_nothread(const char *name, ssc_data_t p_data);

ssc_bool_t ssc_module_exec(ssc_module_t p_mod, ssc_data_t p_data);

typedef void* ssc_handler_t;

ssc_bool_t ssc_module_exec_with_handler(
        ssc_module_t p_mod,
        ssc_data_t p_data,
        ssc_bool_t (*pf_handler)(ssc_module_t, ssc_handler_t, int action, float f0, float f1,
                                 const char *s0, const char *s1, void *user_data),
        void *pf_user_data);

const char *ssc_module_log(ssc_module_t p_mod, int index, int *item_type, float *time);

void __ssc_segfault();
''')
