// Simple wrapper functions
#define BP_WRAP_1(_TYPE, _BP_FUNC, _C_FUNC) template <typename _T> inline _TYPE _BP_FUNC (_T _param) { return _C_FUNC(_param); }
