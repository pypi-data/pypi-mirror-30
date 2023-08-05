//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var SkeletonHelperModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            root: null,
            type: "SkeletonHelper",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.SkeletonHelper(
            this.convertThreeTypeModelToThree(this.get('root'), 'root')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('root');

        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['root'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'SkeletonHelperModel',

    serializers: _.extend({
        root: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    SkeletonHelperModel: SkeletonHelperModel,
};
