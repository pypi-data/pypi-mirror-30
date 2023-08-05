//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ShaderMaterialModel = require('./ShaderMaterial.autogen.js').ShaderMaterialModel;


var ShadowMaterialModel = ShaderMaterialModel.extend({

    defaults: function() {
        return _.extend(ShaderMaterialModel.prototype.defaults.call(this), {

            lights: true,
            transparent: true,
            type: "ShadowMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ShadowMaterial();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ShaderMaterialModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['extensions'] = true;
        this.props_created_by_three['type'] = true;

        this.property_converters['lights'] = 'convertBool';
        this.property_converters['transparent'] = 'convertBool';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'ShadowMaterialModel',

    serializers: _.extend({
    },  ShaderMaterialModel.serializers),
});

module.exports = {
    ShadowMaterialModel: ShadowMaterialModel,
};
