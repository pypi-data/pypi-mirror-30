//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../../_base/Three.js').ThreeModel;


var WebGLShadowMapModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            enabled: false,
            type: "PCFShadowMap",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.WebGLShadowMap();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);

        this.enum_property_types['type'] = 'ShadowTypes';

        this.property_converters['enabled'] = 'convertBool';
        this.property_converters['type'] = 'convertEnum';


    },

}, {

    model_name: 'WebGLShadowMapModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    WebGLShadowMapModel: WebGLShadowMapModel,
};
