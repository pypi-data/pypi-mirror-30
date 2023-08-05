//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var KeyframeTrackModel = require('../KeyframeTrack.autogen.js').KeyframeTrackModel;


var BooleanKeyframeTrackModel = KeyframeTrackModel.extend({

    defaults: function() {
        return _.extend(KeyframeTrackModel.prototype.defaults.call(this), {


        });
    },

    constructThreeObject: function() {

        var result = new THREE.BooleanKeyframeTrack(
            this.get('name'),
            this.convertArrayBufferModelToThree(this.get('times'), 'times'),
            this.convertArrayBufferModelToThree(this.get('values'), 'values'),
            this.convertEnumModelToThree(this.get('interpolation'), 'interpolation')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        KeyframeTrackModel.prototype.createPropertiesArrays.call(this);




    },

}, {

    model_name: 'BooleanKeyframeTrackModel',

    serializers: _.extend({
    },  KeyframeTrackModel.serializers),
});

module.exports = {
    BooleanKeyframeTrackModel: BooleanKeyframeTrackModel,
};
