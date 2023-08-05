//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var AnimationMixerModel = require('./AnimationMixer.autogen.js').AnimationMixerModel;
var AnimationClipModel = require('./AnimationClip.autogen.js').AnimationClipModel;
var ThreeModel = require('../_base/Three.js').ThreeModel;

var AnimationActionModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            mixer: null,
            clip: null,
            localRoot: null,
            clampWhenFinished: false,
            enabled: true,
            loop: "LoopRepeat",
            paused: false,
            repititions: null,
            time: 0,
            timeScale: 1,
            weigth: 1,
            zeroSlopeAtEnd: true,
            zeroSlopeAtStart: true,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.AnimationAction(
            this.convertThreeTypeModelToThree(this.get('mixer'), 'mixer'),
            this.convertThreeTypeModelToThree(this.get('clip'), 'clip'),
            this.convertThreeTypeModelToThree(this.get('localRoot'), 'localRoot')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('mixer');
        this.three_properties.push('clip');
        this.three_properties.push('localRoot');

        this.enum_property_types['loop'] = 'LoopModes';

        this.property_converters['mixer'] = 'convertThreeType';
        this.property_converters['clip'] = 'convertThreeType';
        this.property_converters['localRoot'] = 'convertThreeType';
        this.property_converters['clampWhenFinished'] = 'convertBool';
        this.property_converters['enabled'] = 'convertBool';
        this.property_converters['loop'] = 'convertEnum';
        this.property_converters['paused'] = 'convertBool';
        this.property_converters['repititions'] = null;
        this.property_converters['time'] = 'convertFloat';
        this.property_converters['timeScale'] = 'convertFloat';
        this.property_converters['weigth'] = 'convertFloat';
        this.property_converters['zeroSlopeAtEnd'] = 'convertBool';
        this.property_converters['zeroSlopeAtStart'] = 'convertBool';


    },

}, {

    model_name: 'AnimationActionModel',

    serializers: _.extend({
        mixer: { deserialize: widgets.unpack_models },
        clip: { deserialize: widgets.unpack_models },
        localRoot: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    AnimationActionModel: AnimationActionModel,
};
