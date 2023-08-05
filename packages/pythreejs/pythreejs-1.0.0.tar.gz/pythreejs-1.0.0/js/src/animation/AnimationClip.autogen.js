//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var KeyframeTrackModel = require('./KeyframeTrack.autogen.js').KeyframeTrackModel;

var AnimationClipModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            name: null,
            duration: -1,
            tracks: [],

        });
    },

    constructThreeObject: function() {

        var result = new THREE.AnimationClip(
            this.get('name'),
            this.convertFloatModelToThree(this.get('duration'), 'duration'),
            this.convertThreeTypeArrayModelToThree(this.get('tracks'), 'tracks')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('tracks');

        this.props_created_by_three['duration'] = true;

        this.property_converters['name'] = null;
        this.property_converters['duration'] = 'convertFloat';
        this.property_converters['tracks'] = 'convertThreeTypeArray';


    },

}, {

    model_name: 'AnimationClipModel',

    serializers: _.extend({
        tracks: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    AnimationClipModel: AnimationClipModel,
};
