//
// This file auto-generated with generate-wrappers.js
//
// Load all three.js python wrappers
var loadedModules = [
    require('./WebGLBufferRenderer.autogen.js'),
    require('./WebGLCapabilities.autogen.js'),
    require('./WebGLExtensions.autogen.js'),
    require('./WebGLGeometries.autogen.js'),
    require('./WebGLIndexedBufferRenderer.autogen.js'),
    require('./WebGLLights.autogen.js'),
    require('./WebGLObjects.autogen.js'),
    require('./WebGLProgram.autogen.js'),
    require('./WebGLPrograms.autogen.js'),
    require('./WebGLProperties.autogen.js'),
    require('./WebGLShader.autogen.js'),
    require('./WebGLShadowMap.js'),
    require('./WebGLState.autogen.js'),
];

for (var i in loadedModules) {
    if (loadedModules.hasOwnProperty(i)) {
        var loadedModule = loadedModules[i];
        for (var target_name in loadedModule) {
            if (loadedModule.hasOwnProperty(target_name)) {
                module.exports[target_name] = loadedModule[target_name];
            }
        }
    }
}

