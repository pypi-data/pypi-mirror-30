//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var BoneModel = require('./Bone.autogen.js').BoneModel;

var SkeletonModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            bones: [],

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Skeleton(
            this.convertThreeTypeArrayModelToThree(this.get('bones'), 'bones')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('bones');


        this.property_converters['bones'] = 'convertThreeTypeArray';


    },

}, {

    model_name: 'SkeletonModel',

    serializers: _.extend({
        bones: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    SkeletonModel: SkeletonModel,
};
