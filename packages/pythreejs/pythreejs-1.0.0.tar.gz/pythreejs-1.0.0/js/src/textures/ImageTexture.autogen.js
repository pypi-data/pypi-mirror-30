//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var TextureModel = require('./Texture.autogen.js').TextureModel;


var ImageTextureModel = TextureModel.extend({

    defaults: function() {
        return _.extend(TextureModel.prototype.defaults.call(this), {

            imageUri: "",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.ImageTexture(
            this.get('imageUri'),
            this.convertEnumModelToThree(this.get('mapping'), 'mapping'),
            this.convertEnumModelToThree(this.get('wrapS'), 'wrapS'),
            this.convertEnumModelToThree(this.get('wrapT'), 'wrapT'),
            this.convertEnumModelToThree(this.get('magFilter'), 'magFilter'),
            this.convertEnumModelToThree(this.get('minFilter'), 'minFilter'),
            this.convertEnumModelToThree(this.get('format'), 'format'),
            this.convertEnumModelToThree(this.get('type'), 'type'),
            this.convertFloatModelToThree(this.get('anisotropy'), 'anisotropy')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        TextureModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['id'] = true;
        this.props_created_by_three['version'] = true;

        this.property_converters['imageUri'] = null;


    },

}, {

    model_name: 'ImageTextureModel',

    serializers: _.extend({
    },  TextureModel.serializers),
});

module.exports = {
    ImageTextureModel: ImageTextureModel,
};
