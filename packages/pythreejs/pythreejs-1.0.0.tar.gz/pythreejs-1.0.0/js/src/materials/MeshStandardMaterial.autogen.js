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

var MeshStandardMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            alphaMap: null,
            aoMap: null,
            aoMapIntensity: 1,
            bumpMap: null,
            bumpScale: 1,
            color: "#ffffff",
            defines: {"STANDARD":""},
            displacementMap: null,
            displacementScale: 1,
            displacementBias: 0,
            emissive: "#000000",
            emissiveMap: null,
            emissiveIntensity: 1,
            envMap: null,
            envMapIntensity: 1,
            lightMap: null,
            lightMapIntensity: 1,
            map: null,
            metalness: 0.5,
            metalnessMap: null,
            morphTargets: false,
            morphNormals: false,
            normalMap: null,
            normalScale: [1,1],
            refractionRatio: 0.98,
            roughness: 0.5,
            roughnessMap: null,
            skinning: false,
            wireframe: false,
            wireframeLinecap: "round",
            wireframeLinejoin: "round",
            wireframeLinewidth: 1,
            type: "MeshStandardMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshStandardMaterial(
            {
                alphaMap: this.convertThreeTypeModelToThree(this.get('alphaMap'), 'alphaMap'),
                aoMap: this.convertThreeTypeModelToThree(this.get('aoMap'), 'aoMap'),
                aoMapIntensity: this.convertFloatModelToThree(this.get('aoMapIntensity'), 'aoMapIntensity'),
                bumpMap: this.convertThreeTypeModelToThree(this.get('bumpMap'), 'bumpMap'),
                bumpScale: this.convertFloatModelToThree(this.get('bumpScale'), 'bumpScale'),
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                defines: this.get('defines'),
                displacementMap: this.convertThreeTypeModelToThree(this.get('displacementMap'), 'displacementMap'),
                displacementScale: this.convertFloatModelToThree(this.get('displacementScale'), 'displacementScale'),
                displacementBias: this.convertFloatModelToThree(this.get('displacementBias'), 'displacementBias'),
                emissive: this.convertColorModelToThree(this.get('emissive'), 'emissive'),
                emissiveMap: this.convertThreeTypeModelToThree(this.get('emissiveMap'), 'emissiveMap'),
                emissiveIntensity: this.convertFloatModelToThree(this.get('emissiveIntensity'), 'emissiveIntensity'),
                envMap: this.convertThreeTypeModelToThree(this.get('envMap'), 'envMap'),
                envMapIntensity: this.convertFloatModelToThree(this.get('envMapIntensity'), 'envMapIntensity'),
                lightMap: this.convertThreeTypeModelToThree(this.get('lightMap'), 'lightMap'),
                lightMapIntensity: this.convertFloatModelToThree(this.get('lightMapIntensity'), 'lightMapIntensity'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                metalness: this.convertFloatModelToThree(this.get('metalness'), 'metalness'),
                metalnessMap: this.convertThreeTypeModelToThree(this.get('metalnessMap'), 'metalnessMap'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                morphNormals: this.convertBoolModelToThree(this.get('morphNormals'), 'morphNormals'),
                normalMap: this.convertThreeTypeModelToThree(this.get('normalMap'), 'normalMap'),
                normalScale: this.convertVectorModelToThree(this.get('normalScale'), 'normalScale'),
                refractionRatio: this.convertFloatModelToThree(this.get('refractionRatio'), 'refractionRatio'),
                roughness: this.convertFloatModelToThree(this.get('roughness'), 'roughness'),
                roughnessMap: this.convertThreeTypeModelToThree(this.get('roughnessMap'), 'roughnessMap'),
                skinning: this.convertBoolModelToThree(this.get('skinning'), 'skinning'),
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
        this.three_properties.push('bumpMap');
        this.three_properties.push('displacementMap');
        this.three_properties.push('emissiveMap');
        this.three_properties.push('envMap');
        this.three_properties.push('lightMap');
        this.three_properties.push('map');
        this.three_properties.push('metalnessMap');
        this.three_properties.push('normalMap');
        this.three_properties.push('roughnessMap');

        this.props_created_by_three['type'] = true;

        this.property_converters['alphaMap'] = 'convertThreeType';
        this.property_converters['aoMap'] = 'convertThreeType';
        this.property_converters['aoMapIntensity'] = 'convertFloat';
        this.property_converters['bumpMap'] = 'convertThreeType';
        this.property_converters['bumpScale'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['defines'] = null;
        this.property_converters['displacementMap'] = 'convertThreeType';
        this.property_converters['displacementScale'] = 'convertFloat';
        this.property_converters['displacementBias'] = 'convertFloat';
        this.property_converters['emissive'] = 'convertColor';
        this.property_converters['emissiveMap'] = 'convertThreeType';
        this.property_converters['emissiveIntensity'] = 'convertFloat';
        this.property_converters['envMap'] = 'convertThreeType';
        this.property_converters['envMapIntensity'] = 'convertFloat';
        this.property_converters['lightMap'] = 'convertThreeType';
        this.property_converters['lightMapIntensity'] = 'convertFloat';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['metalness'] = 'convertFloat';
        this.property_converters['metalnessMap'] = 'convertThreeType';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['morphNormals'] = 'convertBool';
        this.property_converters['normalMap'] = 'convertThreeType';
        this.property_converters['normalScale'] = 'convertVector';
        this.property_converters['refractionRatio'] = 'convertFloat';
        this.property_converters['roughness'] = 'convertFloat';
        this.property_converters['roughnessMap'] = 'convertThreeType';
        this.property_converters['skinning'] = 'convertBool';
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinecap'] = null;
        this.property_converters['wireframeLinejoin'] = null;
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['type'] = null;

        this.property_assigners['defines'] = 'assignDict';
        this.property_assigners['normalScale'] = 'assignVector';

    },

}, {

    model_name: 'MeshStandardMaterialModel',

    serializers: _.extend({
        alphaMap: { deserialize: widgets.unpack_models },
        aoMap: { deserialize: widgets.unpack_models },
        bumpMap: { deserialize: widgets.unpack_models },
        displacementMap: { deserialize: widgets.unpack_models },
        emissiveMap: { deserialize: widgets.unpack_models },
        envMap: { deserialize: widgets.unpack_models },
        lightMap: { deserialize: widgets.unpack_models },
        map: { deserialize: widgets.unpack_models },
        metalnessMap: { deserialize: widgets.unpack_models },
        normalMap: { deserialize: widgets.unpack_models },
        roughnessMap: { deserialize: widgets.unpack_models },
    },  MaterialModel.serializers),
});

module.exports = {
    MeshStandardMaterialModel: MeshStandardMaterialModel,
};
