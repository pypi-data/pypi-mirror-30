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

var MeshPhongMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            alphaMap: null,
            aoMap: null,
            aoMapIntensity: 1,
            bumpMap: null,
            bumpScale: 1,
            color: "#ffffff",
            combine: "MultiplyOperation",
            displacementMap: null,
            displacementScale: 1,
            displacementBias: 0,
            emissive: "#000000",
            emissiveMap: null,
            emissiveIntensity: 1,
            envMap: null,
            lightMap: null,
            lightMapIntensity: 1,
            map: null,
            morphNormals: false,
            morphTargets: false,
            normalMap: null,
            normalScale: [1,1],
            reflectivity: 1,
            refractionRatio: 0.98,
            shininess: 30,
            skinning: false,
            specular: "#111111",
            specularMap: null,
            wireframe: false,
            wireframeLinewidth: 1,
            wireframeLinecap: "round",
            wireframeLinejoin: "round",
            type: "MeshPhongMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.MeshPhongMaterial(
            {
                alphaMap: this.convertThreeTypeModelToThree(this.get('alphaMap'), 'alphaMap'),
                aoMap: this.convertThreeTypeModelToThree(this.get('aoMap'), 'aoMap'),
                aoMapIntensity: this.convertFloatModelToThree(this.get('aoMapIntensity'), 'aoMapIntensity'),
                bumpMap: this.convertThreeTypeModelToThree(this.get('bumpMap'), 'bumpMap'),
                bumpScale: this.convertFloatModelToThree(this.get('bumpScale'), 'bumpScale'),
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                combine: this.convertEnumModelToThree(this.get('combine'), 'combine'),
                displacementMap: this.convertThreeTypeModelToThree(this.get('displacementMap'), 'displacementMap'),
                displacementScale: this.convertFloatModelToThree(this.get('displacementScale'), 'displacementScale'),
                displacementBias: this.convertFloatModelToThree(this.get('displacementBias'), 'displacementBias'),
                emissive: this.convertColorModelToThree(this.get('emissive'), 'emissive'),
                emissiveMap: this.convertThreeTypeModelToThree(this.get('emissiveMap'), 'emissiveMap'),
                emissiveIntensity: this.convertFloatModelToThree(this.get('emissiveIntensity'), 'emissiveIntensity'),
                envMap: this.convertThreeTypeModelToThree(this.get('envMap'), 'envMap'),
                lightMap: this.convertThreeTypeModelToThree(this.get('lightMap'), 'lightMap'),
                lightMapIntensity: this.convertFloatModelToThree(this.get('lightMapIntensity'), 'lightMapIntensity'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                morphNormals: this.convertBoolModelToThree(this.get('morphNormals'), 'morphNormals'),
                morphTargets: this.convertBoolModelToThree(this.get('morphTargets'), 'morphTargets'),
                normalMap: this.convertThreeTypeModelToThree(this.get('normalMap'), 'normalMap'),
                normalScale: this.convertVectorModelToThree(this.get('normalScale'), 'normalScale'),
                reflectivity: this.convertFloatModelToThree(this.get('reflectivity'), 'reflectivity'),
                refractionRatio: this.convertFloatModelToThree(this.get('refractionRatio'), 'refractionRatio'),
                shininess: this.convertFloatModelToThree(this.get('shininess'), 'shininess'),
                skinning: this.convertBoolModelToThree(this.get('skinning'), 'skinning'),
                specular: this.convertColorModelToThree(this.get('specular'), 'specular'),
                specularMap: this.convertThreeTypeModelToThree(this.get('specularMap'), 'specularMap'),
                wireframe: this.convertBoolModelToThree(this.get('wireframe'), 'wireframe'),
                wireframeLinewidth: this.convertFloatModelToThree(this.get('wireframeLinewidth'), 'wireframeLinewidth'),
                wireframeLinecap: this.get('wireframeLinecap'),
                wireframeLinejoin: this.get('wireframeLinejoin'),
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
        this.three_properties.push('normalMap');
        this.three_properties.push('specularMap');

        this.props_created_by_three['type'] = true;
        this.enum_property_types['combine'] = 'Operations';

        this.property_converters['alphaMap'] = 'convertThreeType';
        this.property_converters['aoMap'] = 'convertThreeType';
        this.property_converters['aoMapIntensity'] = 'convertFloat';
        this.property_converters['bumpMap'] = 'convertThreeType';
        this.property_converters['bumpScale'] = 'convertFloat';
        this.property_converters['color'] = 'convertColor';
        this.property_converters['combine'] = 'convertEnum';
        this.property_converters['displacementMap'] = 'convertThreeType';
        this.property_converters['displacementScale'] = 'convertFloat';
        this.property_converters['displacementBias'] = 'convertFloat';
        this.property_converters['emissive'] = 'convertColor';
        this.property_converters['emissiveMap'] = 'convertThreeType';
        this.property_converters['emissiveIntensity'] = 'convertFloat';
        this.property_converters['envMap'] = 'convertThreeType';
        this.property_converters['lightMap'] = 'convertThreeType';
        this.property_converters['lightMapIntensity'] = 'convertFloat';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['morphNormals'] = 'convertBool';
        this.property_converters['morphTargets'] = 'convertBool';
        this.property_converters['normalMap'] = 'convertThreeType';
        this.property_converters['normalScale'] = 'convertVector';
        this.property_converters['reflectivity'] = 'convertFloat';
        this.property_converters['refractionRatio'] = 'convertFloat';
        this.property_converters['shininess'] = 'convertFloat';
        this.property_converters['skinning'] = 'convertBool';
        this.property_converters['specular'] = 'convertColor';
        this.property_converters['specularMap'] = 'convertThreeType';
        this.property_converters['wireframe'] = 'convertBool';
        this.property_converters['wireframeLinewidth'] = 'convertFloat';
        this.property_converters['wireframeLinecap'] = null;
        this.property_converters['wireframeLinejoin'] = null;
        this.property_converters['type'] = null;

        this.property_assigners['normalScale'] = 'assignVector';

    },

}, {

    model_name: 'MeshPhongMaterialModel',

    serializers: _.extend({
        alphaMap: { deserialize: widgets.unpack_models },
        aoMap: { deserialize: widgets.unpack_models },
        bumpMap: { deserialize: widgets.unpack_models },
        displacementMap: { deserialize: widgets.unpack_models },
        emissiveMap: { deserialize: widgets.unpack_models },
        envMap: { deserialize: widgets.unpack_models },
        lightMap: { deserialize: widgets.unpack_models },
        map: { deserialize: widgets.unpack_models },
        normalMap: { deserialize: widgets.unpack_models },
        specularMap: { deserialize: widgets.unpack_models },
    },  MaterialModel.serializers),
});

module.exports = {
    MeshPhongMaterialModel: MeshPhongMaterialModel,
};
