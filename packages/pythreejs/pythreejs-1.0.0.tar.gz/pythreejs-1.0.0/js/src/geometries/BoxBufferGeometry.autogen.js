//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;


var BoxBufferGeometryModel = BaseBufferGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseBufferGeometryModel.prototype.defaults.call(this), {

            width: 1,
            height: 1,
            depth: 1,
            widthSegments: 1,
            heightSegments: 1,
            depthSegments: 1,
            type: "BoxBufferGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.BoxBufferGeometry(
            this.convertFloatModelToThree(this.get('width'), 'width'),
            this.convertFloatModelToThree(this.get('height'), 'height'),
            this.convertFloatModelToThree(this.get('depth'), 'depth'),
            this.get('widthSegments'),
            this.get('heightSegments'),
            this.get('depthSegments')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseBufferGeometryModel.prototype.createPropertiesArrays.call(this);

        this.props_created_by_three['type'] = true;

        this.property_converters['width'] = 'convertFloat';
        this.property_converters['height'] = 'convertFloat';
        this.property_converters['depth'] = 'convertFloat';
        this.property_converters['widthSegments'] = null;
        this.property_converters['heightSegments'] = null;
        this.property_converters['depthSegments'] = null;
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'BoxBufferGeometryModel',

    serializers: _.extend({
    },  BaseBufferGeometryModel.serializers),
});

module.exports = {
    BoxBufferGeometryModel: BoxBufferGeometryModel,
};
