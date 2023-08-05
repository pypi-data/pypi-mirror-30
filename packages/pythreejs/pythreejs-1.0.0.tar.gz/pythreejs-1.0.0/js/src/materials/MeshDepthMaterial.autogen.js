//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;

var TextureModel = require('../textures/Texture.autogen.js').TextureModel;

var MeshDepthMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            alphaMap: null,
            displacementMap: null,
            displacementScale: 1,
            displacementBias: 0,
            fog: false,
            lights: false,
            map: null,
            morphTargets: false,
            skinning: false,
            wireframe: false,
            wireframeLinewidth: 1,
            type: "MeshDepthMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshDepthMaterial(
            {
                alphaMap: this.convertThreeTypeModelToThree(this.get('alphaMap'), 'alphaMap'),
                displacementMap: this.convertThreeTypeModelToThree(this.get('displacementMap'), 'displacementMap'),
                displacementScale: this.convertFloatModelToThree(this.get('displacementScale'), 'displacementScale'),
                displacementBias: this.convertFloatModelToThree(this.get('displacementBias'), 'displacementBias'),
                fog: this.convertBoolModelToThree(this.get('fog'), 'fog'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                skinning: this.convertBoolModelToThree(this.get('skinning'), 'skinning'),
                wireframe: this.convertBoolModelToThree(this.get('wireframe'), 'wireframe'),
                wireframeLinewidth: this.convertFloatModelToThree(this.get('wireframeLinewidth'), 'wireframeLinewidth'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('alphaMap');
        this.three_properties.push('displacementMap');
        this.three_properties.push('map');

        this.props_created_by_three['type'] = true;

        this.property_converters['alphaMap'] = 'convertThreeType';
        this.property_converters['displacementMap'] = 'convertThreeType';
        this.property_converters['displacementScale'] = 'convertFloat';
        this.property_converters['displacementBias'] = 'convertFloat';
        this.property_converters['fog'] = 'convertBool';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['skinning'] = 'convertBool';
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'MeshDepthMaterialModel',

    serializers: _.extend({
        alphaMap: { deserialize: widgets.unpack_models },
        displacementMap: { deserialize: widgets.unpack_models },
        map: { deserialize: widgets.unpack_models },
    },  MaterialModel.serializers),
});

module.exports = {
    MeshDepthMaterialModel: MeshDepthMaterialModel,
};
