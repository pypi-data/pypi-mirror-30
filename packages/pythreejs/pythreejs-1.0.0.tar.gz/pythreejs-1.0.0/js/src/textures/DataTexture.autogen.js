//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var TextureModel = require('./Texture.autogen.js').TextureModel;


var DataTextureModel = TextureModel.extend({

    defaults: function() {
        return _.extend(TextureModel.prototype.defaults.call(this), {

            data: null,
            minFilter: "NearestFilter",
            magFilter: "NearestFilter",
            flipY: false,
            generateMipmaps: false,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.DataTexture(
            this.convertArrayBufferModelToThree(this.get('data'), 'data'),
            this.convertEnumModelToThree(this.get('format'), 'format'),
            this.convertEnumModelToThree(this.get('type'), 'type'),
            this.convertEnumModelToThree(this.get('mapping'), 'mapping'),
            this.convertEnumModelToThree(this.get('wrapS'), 'wrapS'),
            this.convertEnumModelToThree(this.get('wrapT'), 'wrapT'),
            this.convertEnumModelToThree(this.get('magFilter'), 'magFilter'),
            this.convertEnumModelToThree(this.get('minFilter'), 'minFilter'),
            this.convertFloatModelToThree(this.get('anisotropy'), 'anisotropy')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        TextureModel.prototype.createPropertiesArrays.call(this);
        this.datawidget_properties.push('data');

        this.props_created_by_three['id'] = true;
        this.props_created_by_three['version'] = true;
        this.enum_property_types['minFilter'] = 'Filters';
        this.enum_property_types['magFilter'] = 'Filters';

        this.property_converters['data'] = 'convertArrayBuffer';
        this.property_converters['minFilter'] = 'convertEnum';
        this.property_converters['magFilter'] = 'convertEnum';
        this.property_converters['flipY'] = 'convertBool';
        this.property_converters['generateMipmaps'] = 'convertBool';


    },

}, {

    model_name: 'DataTextureModel',

    serializers: _.extend({
        data: dataserializers.data_union_serialization,
    },  TextureModel.serializers),
});

module.exports = {
    DataTextureModel: DataTextureModel,
};
