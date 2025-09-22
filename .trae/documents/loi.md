
D:\tool\tool auto\web-dashboard>pip instal requirements.txt
ERROR: unknown command "instal" - maybe you meant "install"

D:\tool\tool auto\web-dashboard>npm run dev

> web-dashboard@0.1.0 dev
> next dev --turbo

 ⚠ Warning: Next.js inferred your workspace root, but it may not be correct.
 We detected multiple lockfiles and selected the directory of D:\tool\tool auto\package-lock.json as the root directory.
 To silence this warning, set `turbopack.root` in your Next.js config, or consider removing one of the lockfiles if it's not needed.
   See https://nextjs.org/docs/app/api-reference/config/next-config-js/turbopack#root-directory for more information.
 Detected additional lockfiles:
   * D:\tool\tool auto\web-dashboard\package-lock.json

   ▲ Next.js 15.5.3 (Turbopack)
   - Local:        http://localhost:3000
   - Network:      http://192.168.4.227:3000
   - Environments: .env.local, .env
   - Experiments (use with caution):
     ✓ optimizeCss
     · optimizePackageImports

 ✓ Starting...
 ✓ Ready in 1887ms
 ○ Compiling / ...

-----
FATAL: An unexpected Turbopack error occurred. A panic log has been written to C:\Users\BOXPHONE\AppData\Local\Temp\next-panic-e4f48f6c9e62508510bcde5d7b2b9095.log.

To help make Turbopack better, report this error by clicking here: https://github.com/vercel/next.js/discussions/new?category=turbopack-error-report&title=Turbopack%20Error%3A%20Failed%20to%20write%20app%20endpoint%20%2Fpage&body=Turbopack%20version%3A%20%60db56d775%60%0ANext.js%20version%3A%20%600.0.0%60%0A%0AError%20message%3A%0A%60%60%60%0ATurbopack%20Error%3A%20Failed%20to%20write%20app%20endpoint%20%2Fpage%0A%60%60%60&labels=Turbopack,Turbopack%20Panic%20Backtrace
-----

 ✓ Compiled / in 19.4s
 ○ Compiling /_error ...
 ✓ Compiled /_error in 2.3s
 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\compiled\next-server\pages-turbo.runtime.dev.js
- D:\tool\tool auto\web-dashboard\.next\server\chunks\ssr\[root-of-the-server]__e6a4d965._.js
- D:\tool\tool auto\web-dashboard\.next\server\chunks\ssr\[turbopack]_runtime.js
- D:\tool\tool auto\web-dashboard\.next\server\pages\_document.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\require.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\utils.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\swc\options.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\swc\index.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\analysis\parse-module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\analysis\get-page-static-info.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\router-utils\setup-dev-bundler.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\router-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\compiled\next-server\pages-turbo.runtime.dev.js
- D:\tool\tool auto\web-dashboard\.next\server\chunks\ssr\[root-of-the-server]__e6a4d965._.js
- D:\tool\tool auto\web-dashboard\.next\server\chunks\ssr\[turbopack]_runtime.js
- D:\tool\tool auto\web-dashboard\.next\server\pages\_document.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\require.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\utils.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\swc\options.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\swc\index.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\analysis\parse-module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\build\analysis\get-page-static-info.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\router-utils\setup-dev-bundler.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\router-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
 GET / 500 in 40114ms

-----
FATAL: An unexpected Turbopack error occurred. A panic log has been written to C:\Users\BOXPHONE\AppData\Local\Temp\next-panic-e4f48f6c9e62508510bcde5d7b2b9095.log.

To help make Turbopack better, report this error by clicking here: https://github.com/vercel/next.js/discussions/new?category=turbopack-error-report&title=Turbopack%20Error%3A%20Failed%20to%20write%20app%20endpoint%20%2Fpage&body=Turbopack%20version%3A%20%60db56d775%60%0ANext.js%20version%3A%20%600.0.0%60%0A%0AError%20message%3A%0A%60%60%60%0ATurbopack%20Error%3A%20Failed%20to%20write%20app%20endpoint%20%2Fpage%0A%60%60%60&labels=Turbopack,Turbopack%20Panic%20Backtrace
-----

 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
Error [TurbopackInternalError]: Failed to write app endpoint /page

Caused by:
- [project]/web-dashboard/src/app/globals.css [app-client] (css)
- creating new process
- reading packet length
- An existing connection was forcibly closed by the remote host. (os error 10054)

Debug info:
- Execution of TaskId { id: 2147483652 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /page
- Execution of AppEndpoint::output failed
- Execution of AppProject::app_module_graphs failed
- Execution of *<AppEndpoint as Endpoint>::additional_entries failed
- Execution of *ModuleGraph::from_graphs failed
- Execution of SingleModuleGraph::new_with_entries_visited_intern failed
- [project]/web-dashboard/src/app/globals.css [app-client] (css)
- Execution of primary_chunkable_referenced_modules failed
- Execution of <CssModuleAsset as Module>::references failed
- Execution of parse_css failed
- Execution of <PostCssTransformedAsset as Asset>::content failed
- Execution of PostCssTransformedAsset::process failed
- creating new process
- reading packet length
- An existing connection was forcibly closed by the remote host. (os error 10054)
    at <unknown> (TurbopackInternalError: Failed to write app endpoint /page) {
  location: undefined
}
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
Error [TurbopackInternalError]: Failed to write app endpoint /page

Caused by:
- [project]/web-dashboard/src/app/globals.css [app-client] (css)
- creating new process
- reading packet length
- An existing connection was forcibly closed by the remote host. (os error 10054)

Debug info:
- Execution of TaskId { id: 2147483676 } transient failed
- Execution of get_written_endpoint_with_issues_operation failed
- Execution of endpoint_write_to_disk failed
- Execution of <AppEndpoint as Endpoint>::output failed
- Failed to write app endpoint /page
- Execution of AppEndpoint::output failed
- Execution of AppProject::app_module_graphs failed
- Execution of *<AppEndpoint as Endpoint>::additional_entries failed
- Execution of *ModuleGraph::from_graphs failed
- Execution of SingleModuleGraph::new_with_entries_visited_intern failed
- [project]/web-dashboard/src/app/globals.css [app-client] (css)
- Execution of primary_chunkable_referenced_modules failed
- Execution of <CssModuleAsset as Module>::references failed
- Execution of parse_css failed
- Execution of <PostCssTransformedAsset as Asset>::content failed
- Execution of PostCssTransformedAsset::process failed
- creating new process
- reading packet length
- An existing connection was forcibly closed by the remote host. (os error 10054)
    at <unknown> (TurbopackInternalError: Failed to write app endpoint /page) {
  location: undefined
}
 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
[Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [TypeError: __webpack_require__(...) is not a constructor]
 ⨯ [Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
[Error: Cannot find module 'critters'
Require stack:
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\post-process.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\render.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\module.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\route-modules\pages\builtin\_error.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\load-default-error-components.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\dev\next-dev-server.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\next.js
- D:\tool\tool auto\web-dashboard\node_modules\next\dist\server\lib\start-server.js] {
  code: 'MODULE_NOT_FOUND',
  requireStack: [Array]
}
 GET / 500 in 903ms
 GET / 500 in 324ms
 ○ Compiling /favicon.ico ...
 ✓ Compiled /favicon.ico in 906ms
 GET /favicon.ico 200 in 2482ms
