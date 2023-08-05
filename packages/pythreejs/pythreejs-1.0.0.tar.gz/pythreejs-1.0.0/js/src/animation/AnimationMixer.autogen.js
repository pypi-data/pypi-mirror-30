//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var ThreeModel = require('../_base/Three.js').ThreeModel;

var AnimationMixerModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            rootObject: null,
            time: 0,
            timeScale: 1,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.AnimationMixer(
            this.convertThreeTypeModelToThree(this.get('rootObject'), 'rootObject'),
            this.convertFloatModelToThree(this.get('time'), 'time'),
            this.convertFloatModelToThree(this.get('timeScale'), 'timeScale')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('rootObject');


        this.property_converters['rootObject'] = 'convertThreeType';
        this.property_converters['time'] = 'convertFloat';
        this.property_converters['timeScale'] = 'convertFloat';


    },

}, {

    model_name: 'AnimationMixerModel',

    serializers: _.extend({
        rootObject: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    AnimationMixerModel: AnimationMixerModel,
};
