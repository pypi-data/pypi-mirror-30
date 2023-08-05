//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var Object3DModel = require('../core/Object3D.js').Object3DModel;

var MaterialModel = require('../materials/Material.js').MaterialModel;
var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;
var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;

var MeshModel = Object3DModel.extend({

    defaults: function() {
        return _.extend(Object3DModel.prototype.defaults.call(this), {

            material: [],
            geometry: null,
            drawMode: "TrianglesDrawMode",
            morphTargetInfluences: [],
            type: "Mesh",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.Mesh(
            this.convertThreeTypeModelToThree(this.get('geometry'), 'geometry'),
            this.convertThreeTypeArrayModelToThree(this.get('material'), 'material')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        Object3DModel.prototype.createPropertiesArrays.call(this);
        this.three_nested_properties.push('material');
        this.three_properties.push('geometry');

        this.props_created_by_three['morphTargetInfluences'] = true;
        this.props_created_by_three['type'] = true;
        this.props_created_by_three['rotation'] = true;
        this.props_created_by_three['quaternion'] = true;
        this.props_created_by_three['matrixWorldNeedsUpdate'] = true;
        this.enum_property_types['drawMode'] = 'DrawModes';

        this.property_converters['material'] = 'convertThreeTypeArray';
        this.property_converters['geometry'] = 'convertThreeType';
        this.property_converters['drawMode'] = 'convertEnum';
        this.property_converters['morphTargetInfluences'] = null;
        this.property_converters['type'] = null;

        this.property_assigners['morphTargetInfluences'] = 'assignArray';

    },

}, {

    model_name: 'MeshModel',

    serializers: _.extend({
        material: { deserialize: widgets.unpack_models },
        geometry: { deserialize: widgets.unpack_models },
    },  Object3DModel.serializers),
});

module.exports = {
    MeshModel: MeshModel,
};
