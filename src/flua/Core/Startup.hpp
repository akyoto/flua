// Simple wrapper functions
#define BP_WRAP_1(_TYPE, _BP_FUNC, _C_FUNC) template <typename _T> inline _TYPE _BP_FUNC (_T _param) { return _C_FUNC(_param); }
#define BP_WRAP_2(_TYPE, _BP_FUNC, _C_FUNC) template <typename _T1, typename _T2> inline _TYPE _BP_FUNC (_T1 _param1, _T2 _param2) { return _C_FUNC(_param1, _param2); }
