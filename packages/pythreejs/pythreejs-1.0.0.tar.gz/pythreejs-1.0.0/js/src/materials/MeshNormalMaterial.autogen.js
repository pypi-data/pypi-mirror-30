//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;


var MeshNormalMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            fog: false,
            lights: false,
            morphTargets: false,
            wireframe: false,
            wireframeLinewidth: 1,
            type: "MeshNormalMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshNormalMaterial(
            {
                fog: this.convertBoolModelToThree(this.get('fog'), 'fog'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                wireframe: this.convertBoolModelToThree(this.get('wireframe'), 'wireframe'),
                wireframeLinewidth: this.convertFloatModelToThree(this.get('wireframeLinewidth'), 'wireframeLinewidth'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['fog'] = 'convertBool';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'MeshNormalMaterialModel',

    serializers: _.extend({
    },  MaterialModel.serializers),
});

module.exports = {
    MeshNormalMaterialModel: MeshNormalMaterialModel,
};
