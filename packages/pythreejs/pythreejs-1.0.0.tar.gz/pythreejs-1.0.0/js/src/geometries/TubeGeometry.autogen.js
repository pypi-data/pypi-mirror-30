//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;

var CurveModel = require('../extras/core/Curve.autogen.js').CurveModel;

var TubeGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            path: null,
            segments: 64,
            radius: 1,
            radiusSegments: 8,
            close: false,
            type: "TubeGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.TubeGeometry(
            this.convertThreeTypeModelToThree(this.get('path'), 'path'),
            this.get('segments'),
            this.convertFloatModelToThree(this.get('radius'), 'radius'),
            this.get('radiusSegments'),
            this.convertBoolModelToThree(this.get('close'), 'close')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('path');

        this.props_created_by_three['type'] = true;

        this.property_converters['path'] = 'convertThreeType';
        this.property_converters['segments'] = null;
        this.property_converters['radius'] = 'convertFloat';
        this.property_converters['radiusSegments'] = null;
        this.property_converters['close'] = 'convertBool';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'TubeGeometryModel',

    serializers: _.extend({
        path: { deserialize: widgets.unpack_models },
    },  BaseGeometryModel.serializers),
});

module.exports = {
    TubeGeometryModel: TubeGeometryModel,
};
