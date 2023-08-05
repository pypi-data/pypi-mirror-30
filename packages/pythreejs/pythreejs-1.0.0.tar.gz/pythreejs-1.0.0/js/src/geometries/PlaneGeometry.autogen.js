//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;


var PlaneGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            width: 1,
            height: 1,
            widthSegments: 1,
            heightSegments: 1,
            type: "PlaneGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.PlaneGeometry(
            this.convertFloatModelToThree(this.get('width'), 'width'),
            this.convertFloatModelToThree(this.get('height'), 'height'),
            this.get('widthSegments'),
            this.get('heightSegments')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['width'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['widthSegments'] = null;
        this.property_converters['heightSegments'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'PlaneGeometryModel',

    serializers: _.extend({
    },  BaseGeometryModel.serializers),
});

module.exports = {
    PlaneGeometryModel: PlaneGeometryModel,
};
