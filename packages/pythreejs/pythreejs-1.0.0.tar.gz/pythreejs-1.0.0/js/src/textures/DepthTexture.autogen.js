//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var TextureModel = require('./Texture.autogen.js').TextureModel;


var DepthTextureModel = TextureModel.extend({

    defaults: function() {
        return _.extend(TextureModel.prototype.defaults.call(this), {

            width: 0,
            height: 0,
            format: "DepthFormat",
            type: "UnsignedShortType",
            minFilter: "NearestFilter",
            magFilter: "NearestFilter",
            flipY: false,
            generateMipmaps: false,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.DepthTexture(
            this.get('width'),
            this.get('height'),
            this.convertEnumModelToThree(this.get('type'), 'type'),
            this.convertEnumModelToThree(this.get('wrapS'), 'wrapS'),
            this.convertEnumModelToThree(this.get('wrapT'), 'wrapT'),
            this.convertEnumModelToThree(this.get('magFilter'), 'magFilter'),
            this.convertEnumModelToThree(this.get('minFilter'), 'minFilter'),
            this.convertFloatModelToThree(this.get('anisotropy'), 'anisotropy'),
            this.convertEnumModelToThree(this.get('format'), 'format')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        TextureModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['id'] = true;
        this.props_created_by_three['version'] = true;
        this.enum_property_types['format'] = 'DepthFormats';
        this.enum_property_types['type'] = 'DataTypes';
        this.enum_property_types['minFilter'] = 'Filters';
        this.enum_property_types['magFilter'] = 'Filters';

        this.property_converters['width'] = null;
        this.property_converters['height'] = null;
        this.property_converters['format'] = 'convertEnum';
        this.property_converters['type'] = 'convertEnum';
        this.property_converters['minFilter'] = 'convertEnum';
        this.property_converters['magFilter'] = 'convertEnum';
        this.property_converters['flipY'] = 'convertBool';
        this.property_converters['generateMipmaps'] = 'convertBool';


    },

}, {

    model_name: 'DepthTextureModel',

    serializers: _.extend({
    },  TextureModel.serializers),
});

module.exports = {
    DepthTextureModel: DepthTextureModel,
};
