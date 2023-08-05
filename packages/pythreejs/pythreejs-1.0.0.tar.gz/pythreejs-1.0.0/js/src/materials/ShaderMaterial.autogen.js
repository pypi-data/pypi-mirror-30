//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;


var ShaderMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            uniforms: {},
            clipping: false,
            extensions: {},
            fog: false,
            fragmentShader: "",
            lights: false,
            linewidth: 1,
            morphNormals: false,
            morphTargets: false,
            flatShading: false,
            skinning: false,
            uniformsNeedUpdate: false,
            vertexShader: "",
            wireframe: false,
            wireframeLinewidth: 1,
            type: "ShaderMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ShaderMaterial(
            {
                uniforms: this.convertUniformDictModelToThree(this.get('uniforms'), 'uniforms'),
                clipping: this.convertBoolModelToThree(this.get('clipping'), 'clipping'),
                extensions: this.get('extensions'),
                fog: this.convertBoolModelToThree(this.get('fog'), 'fog'),
                fragmentShader: this.get('fragmentShader'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                linewidth: this.convertFloatModelToThree(this.get('linewidth'), 'linewidth'),
                morphNormals: this.convertBoolModelToThree(this.get('morphNormals'), 'morphNormals'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                flatShading: this.convertBoolModelToThree(this.get('flatShading'), 'flatShading'),
                skinning: this.convertBoolModelToThree(this.get('skinning'), 'skinning'),
                uniformsNeedUpdate: this.convertBoolModelToThree(this.get('uniformsNeedUpdate'), 'uniformsNeedUpdate'),
                vertexShader: this.get('vertexShader'),
                wireframe: this.convertBoolModelToThree(this.get('wireframe'), 'wireframe'),
                wireframeLinewidth: this.convertFloatModelToThree(this.get('wireframeLinewidth'), 'wireframeLinewidth'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['extensions'] = true;
        this.props_created_by_three['type'] = true;

        this.property_converters['uniforms'] = 'convertUniformDict';
        this.property_converters['clipping'] = 'convertBool';
        this.property_converters['extensions'] = null;
        this.property_converters['fog'] = 'convertBool';
        this.property_converters['fragmentShader'] = null;
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['linewidth'] = 'convertFloat';
        this.property_converters['morphNormals'] = 'convertBool';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['flatShading'] = 'convertBool';
        this.property_converters['skinning'] = 'convertBool';
        this.property_converters['uniformsNeedUpdate'] = 'convertBool';
        this.property_converters['vertexShader'] = null;
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['type'] = null;

        this.property_assigners['uniforms'] = 'assignDict';
        this.property_assigners['extensions'] = 'assignDict';

    },

}, {

    model_name: 'ShaderMaterialModel',

    serializers: _.extend({
    },  MaterialModel.serializers),
});

module.exports = {
    ShaderMaterialModel: ShaderMaterialModel,
};
