//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var MeshModel = require('./Mesh.js').MeshModel;

var SkeletonModel = require('./Skeleton.autogen.js').SkeletonModel;

var SkinnedMeshModel = MeshModel.extend({

    defaults: function() {
        return _.extend(MeshModel.prototype.defaults.call(this), {

            bindMode: "attached",
            bindMatrix: [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
            skeleton: null,
            type: "SkinnedMesh",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.SkinnedMesh(
            this.convertThreeTypeModelToThree(this.get('geometry'), 'geometry'),
            this.convertThreeTypeArrayModelToThree(this.get('material'), 'material')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        MeshModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('skeleton');

        this.props_created_by_three['morphTargetInfluences'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;

        this.property_converters['bindMode'] = null;
        this.property_converters['bindMatrix'] = 'convertMatrix';
        this.property_converters['skeleton'] = 'convertThreeType';
        this.property_converters['type'] = null;

        this.property_assigners['bindMatrix'] = 'assignMatrix';

    },

}, {

    model_name: 'SkinnedMeshModel',

    serializers: _.extend({
        skeleton: { deserialize: widgets.unpack_models },
    },  MeshModel.serializers),
});

module.exports = {
    SkinnedMeshModel: SkinnedMeshModel,
};
