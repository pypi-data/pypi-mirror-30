//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;

var BaseGeometryModel = require('../core/BaseGeometry.autogen.js').BaseGeometryModel;
var BaseBufferGeometryModel = require('../core/BaseBufferGeometry.autogen.js').BaseBufferGeometryModel;

var WireframeGeometryModel = BaseGeometryModel.extend({

    defaults: function() {
        return _.extend(BaseGeometryModel.prototype.defaults.call(this), {

            geometry: null,
            type: "WireframeGeometry",

        });
    },

    constructThreeObject: function() {

        var result = new THREE.WireframeGeometry(
            this.convertThreeTypeModelToThree(this.get('geometry'), 'geometry')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        BaseGeometryModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('geometry');

        this.props_created_by_three['type'] = true;

        this.property_converters['geometry'] = 'convertThreeType';
        this.property_converters['type'] = null;


    },

}, {

    model_name: 'WireframeGeometryModel',

    serializers: _.extend({
        geometry: { deserialize: widgets.unpack_models },
    },  BaseGeometryModel.serializers),
});

module.exports = {
    WireframeGeometryModel: WireframeGeometryModel,
};
