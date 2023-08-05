//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ControlsModel = require('./Controls.autogen.js').ControlsModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var PickerModel = ControlsModel.extend({

    defaults: function() {
        return _.extend(ControlsModel.prototype.defaults.call(this), {

            event: "click",
            all: false,
            distance: null,
            point: [0,0,0],
            face: [0,0,0],
            faceNormal: [0,0,0],
            faceVertices: [],
            faceIndex: 0,
            modifiers: [],
            object: null,
            picked: [],
            uv: [0,0],
            indices: [],

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Picker(
            this.convertThreeTypeModelToThree(this.get('controlling'), 'controlling')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ControlsModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('object');

        this.props_created_by_three['distance'] = true;
        this.props_created_by_three['point'] = true;
        this.props_created_by_three['face'] = true;
        this.props_created_by_three['faceNormal'] = true;
        this.props_created_by_three['faceVertices'] = true;
        this.props_created_by_three['faceIndex'] = true;
        this.props_created_by_three['object'] = true;
        this.props_created_by_three['picked'] = true;
        this.props_created_by_three['uv'] = true;
        this.props_created_by_three['indices'] = true;

        this.property_converters['event'] = null;
        this.property_converters['all'] = 'convertBool';
        this.property_converters['distance'] = 'convertFloat';
        this.property_converters['point'] = 'convertVector';
        this.property_converters['face'] = 'convertVector';
        this.property_converters['faceNormal'] = 'convertVector';
        this.property_converters['faceVertices'] = 'convertVectorArray';
        this.property_converters['faceIndex'] = null;
        this.property_converters['modifiers'] = null;
        this.property_converters['object'] = 'convertThreeType';
        this.property_converters['picked'] = null;
        this.property_converters['uv'] = 'convertVector';
        this.property_converters['indices'] = null;

        this.property_assigners['point'] = 'assignVector';
        this.property_assigners['face'] = 'assignVector';
        this.property_assigners['faceNormal'] = 'assignVector';
        this.property_assigners['faceVertices'] = 'assignArray';
        this.property_assigners['modifiers'] = 'assignArray';
        this.property_assigners['picked'] = 'assignArray';
        this.property_assigners['uv'] = 'assignVector';
        this.property_assigners['indices'] = 'assignArray';

    },

}, {

    model_name: 'PickerModel',

    serializers: _.extend({
        object: { deserialize: widgets.unpack_models },
    },  ControlsModel.serializers),
});

module.exports = {
    PickerModel: PickerModel,
};
