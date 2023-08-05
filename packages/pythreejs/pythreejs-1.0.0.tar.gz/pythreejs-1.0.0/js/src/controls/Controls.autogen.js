//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var ControlsModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            controlling: null,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Controls();
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('controlling');


        this.property_converters['controlling'] = 'convertThreeType';


    },

}, {

    model_name: 'ControlsModel',

    serializers: _.extend({
        controlling: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    ControlsModel: ControlsModel,
};
