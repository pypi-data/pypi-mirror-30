//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MaterialModel = require('./Material.js').MaterialModel;

var TextureModel = require('../textures/Texture.autogen.js').TextureModel;

var PointsMaterialModel = MaterialModel.extend({

    defaults: function() {
        return _.extend(MaterialModel.prototype.defaults.call(this), {

            color: "#ffffff",
            lights: false,
            map: null,
            size: 1,
            sizeAttenuation: true,
            type: "PointsMaterial",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PointsMaterial(
            {
                color: this.convertColorModelToThree(this.get('color'), 'color'),
                lights: this.convertBoolModelToThree(this.get('lights'), 'lights'),
                map: this.convertThreeTypeModelToThree(this.get('map'), 'map'),
                size: this.convertFloatModelToThree(this.get('size'), 'size'),
                sizeAttenuation: this.convertBoolModelToThree(this.get('sizeAttenuation'), 'sizeAttenuation'),
                type: this.get('type'),
            }
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MaterialModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('map');

        this.props_created_by_three['type'] = true;

        this.property_converters['color'] = 'convertColor';
        this.property_converters['lights'] = 'convertBool';
        this.property_converters['map'] = 'convertThreeType';
        this.property_converters['size'] = 'convertFloat';
        this.property_converters['sizeAttenuation'] = 'convertBool';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PointsMaterialModel',

    serializers: _.extend({
        map: { deserialize: widgets.unpack_models },
    },  MaterialModel.serializers),
});

module.exports = {
    PointsMaterialModel: PointsMaterialModel,
};
