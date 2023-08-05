//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;


var KeyframeTrackModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: "",
            times: null,
            values: null,
            interpolation: "InterpolateLinear",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.KeyframeTrack(
            this.get('name'),
            this.convertArrayBufferModelToThree(this.get('times'), 'times'),
            this.convertArrayBufferModelToThree(this.get('values'), 'values'),
            this.convertEnumModelToThree(this.get('interpolation'), 'interpolation')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.datawidget_properties.push('times');
        this.datawidget_properties.push('values');

        this.enum_property_types['interpolation'] = 'InterpolationModes';

        this.property_converters['name'] = null;
        this.property_converters['times'] = 'convertArrayBuffer';
        this.property_converters['values'] = 'convertArrayBuffer';
        this.property_converters['interpolation'] = 'convertEnum';


    },

}, {

    model_name: 'KeyframeTrackModel',

    serializers: _.extend({
        times: dataserializers.data_union_serialization,
        values: dataserializers.data_union_serialization,
    },  ThreeModel.serializers),
});

module.exports = {
    KeyframeTrackModel: KeyframeTrackModel,
};
