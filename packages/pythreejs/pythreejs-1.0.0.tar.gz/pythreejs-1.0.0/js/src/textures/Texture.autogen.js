//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var TextureModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            mapping: "UVMapping",
            wrapS: "ClampToEdgeWrapping",
            wrapT: "ClampToEdgeWrapping",
            magFilter: "LinearFilter",
            minFilter: "LinearMipMapLinearFilter",
            format: "RGBAFormat",
            type: "UnsignedByteType",
            anisotropy: 1,
            repeat: [1,1],
            offset: [0,0],
            generateMipmaps: true,
            premultiplyAlpha: false,
            flipY: true,
            unpackAlignment: 4,
            encoding: "LinearEncoding",
            version: 0,
            rotation: 0,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Texture();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['id'] = true;
        this.props_created_by_three['version'] = true;
        this.enum_property_types['mapping'] = 'MappingModes';
        this.enum_property_types['wrapS'] = 'WrappingModes';
        this.enum_property_types['wrapT'] = 'WrappingModes';
        this.enum_property_types['magFilter'] = 'Filters';
        this.enum_property_types['minFilter'] = 'Filters';
        this.enum_property_types['format'] = 'PixelFormats';
        this.enum_property_types['type'] = 'DataTypes';
        this.enum_property_types['encoding'] = 'TextureEncodings';

        this.property_converters['name'] = null;
        this.property_converters['mapping'] = 'convertEnum';
        this.property_converters['wrapS'] = 'convertEnum';
        this.property_converters['wrapT'] = 'convertEnum';
        this.property_converters['magFilter'] = 'convertEnum';
        this.property_converters['minFilter'] = 'convertEnum';
        this.property_converters['format'] = 'convertEnum';
        this.property_converters['type'] = 'convertEnum';
        this.property_converters['anisotropy'] = 'convertFloat';
        this.property_converters['repeat'] = 'convertVector';
        this.property_converters['offset'] = 'convertVector';
        this.property_converters['generateMipmaps'] = 'convertBool';
        this.property_converters['premultiplyAlpha'] = 'convertBool';
        this.property_converters['flipY'] = 'convertBool';
        this.property_converters['unpackAlignment'] = null;
        this.property_converters['encoding'] = 'convertEnum';
        this.property_converters['version'] = null;
        this.property_converters['rotation'] = 'convertFloat';

        this.property_assigners['repeat'] = 'assignVector';
        this.property_assigners['offset'] = 'assignVector';

    },

}, {

    model_name: 'TextureModel',

    serializers: _.extend({
    },  ThreeModel.serializers),
});

module.exports = {
    TextureModel: TextureModel,
};
