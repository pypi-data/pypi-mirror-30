//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;

var TextureModel = require('../textures/Texture.autogen.js').TextureModel;
var CubeTextureModel = require('../textures/CubeTexture.autogen.js').CubeTextureModel;

var MeshLambertMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            alphaMap: null,
            aoMap: null,
            aoMapIntensity: 1,
            color: "#ffffff",
            combine: "MultiplyOperation",
            emissive: "#000000",
            emissiveMap: null,
            emissiveIntensity: 1,
            envMap: null,
            lightMap: null,
            lightMapIntensity: 1,
            map: null,
            morphNormals: false,
            morphTargets: false,
            reflectivity: 1,
            refractionRatio: 0.98,
            skinning: false,
            specularMap: null,
            wireframe: false,
            wireframeLinecap: "round",
            wireframeLinejoin: "round",
            wireframeLinewidth: 1,
            type: "MeshLambertMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshLambertMaterial(
            {
                alphaMap: this.convertThreeTypeModelToThree(this.get('alphaMap'), 'alphaMap'),
                aoMap: this.convertThreeTypeModelToThree(this.get('aoMap'), 'aoMap'),
                aoMapIntensity: this.convertFloatModelToThree(this.get('aoMapIntensity'), 'aoMapIntensity'),
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                combine: this.convertEnumModelToThree(this.get('combine'), 'combine'),
                emissive: this.convertColorModelToThree(this.get('emissive'), 'emissive'),
                emissiveMap: this.convertThreeTypeModelToThree(this.get('emissiveMap'), 'emissiveMap'),
                emissiveIntensity: this.convertFloatModelToThree(this.get('emissiveIntensity'), 'emissiveIntensity'),
                envMap: this.convertThreeTypeModelToThree(this.get('envMap'), 'envMap'),
                lightMap: this.convertThreeTypeModelToThree(this.get('lightMap'), 'lightMap'),
                lightMapIntensity: this.convertFloatModelToThree(this.get('lightMapIntensity'), 'lightMapIntensity'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                morphNormals: this.convertBoolModelToThree(this.get('morphNormals'), 'morphNormals'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                reflectivity: this.convertFloatModelToThree(this.get('reflectivity'), 'reflectivity'),
                refractionRatio: this.convertFloatModelToThree(this.get('refractionRatio'), 'refractionRatio'),
                skinning: this.convertBoolModelToThree(this.get('skinning'), 'skinning'),
                specularMap: this.convertThreeTypeModelToThree(this.get('specularMap'), 'specularMap'),
                wireframe: this.convertBoolModelToThree(this.get('wireframe'), 'wireframe'),
                wireframeLinecap: this.get('wireframeLinecap'),
                wireframeLinejoin: this.get('wireframeLinejoin'),
                wireframeLinewidth: this.convertFloatModelToThree(this.get('wireframeLinewidth'), 'wireframeLinewidth'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('alphaMap');
        this.three_properties.push('aoMap');
        this.three_properties.push('emissiveMap');
        this.three_properties.push('envMap');
        this.three_properties.push('lightMap');
        this.three_properties.push('map');
        this.three_properties.push('specularMap');

        this.props_created_by_three['type'] = true;
        this.enum_property_types['combine'] = 'Operations';

        this.property_converters['alphaMap'] = 'convertThreeType';
        this.property_converters['aoMap'] = 'convertThreeType';
        this.property_converters['aoMapIntensity'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['combine'] = 'convertEnum';
        this.property_converters['emissive'] = 'convertColor';
        this.property_converters['emissiveMap'] = 'convertThreeType';
        this.property_converters['emissiveIntensity'] = 'convertFloat';
        this.property_converters['envMap'] = 'convertThreeType';
        this.property_converters['lightMap'] = 'convertThreeType';
        this.property_converters['lightMapIntensity'] = 'convertFloat';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['morphNormals'] = 'convertBool';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['reflectivity'] = 'convertFloat';
        this.property_converters['refractionRatio'] = 'convertFloat';
        this.property_converters['skinning'] = 'convertBool';
        this.property_converters['specularMap'] = 'convertThreeType';
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinecap'] = null;
        this.property_converters['wireframeLinejoin'] = null;
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'MeshLambertMaterialModel',

    serializers: _.extend({
        alphaMap: { deserialize: widgets.unpack_models },
        aoMap: { deserialize: widgets.unpack_models },
        emissiveMap: { deserialize: widgets.unpack_models },
        envMap: { deserialize: widgets.unpack_models },
        lightMap: { deserialize: widgets.unpack_models },
        map: { deserialize: widgets.unpack_models },
        specularMap: { deserialize: widgets.unpack_models },
    },  MaterialModel.serializers),
});

module.exports = {
    MeshLambertMaterialModel: MeshLambertMaterialModel,
};
