//
// This file auto-generated with generate-wrappers.js
//

var _ = require('underscore');
var THREE = require('three');
var widgets = require('@jupyter-widgets/base');
var dataserializers = require('jupyter-dataserializers');

var ThreeModel = require('../_base/Three.js').ThreeModel;

var InterleavedBufferModel = require('./InterleavedBuffer.autogen.js').InterleavedBufferModel;

var InterleavedBufferAttributeModel = ThreeModel.extend({

    defaults: function() {
        return _.extend(ThreeModel.prototype.defaults.call(this), {

            data: null,
            itemSize: 0,
            offset: 0,
            normalized: true,

        });
    },

    constructThreeObject: function() {

        var result = new THREE.InterleavedBufferAttribute(
            this.convertThreeTypeModelToThree(this.get('data'), 'data'),
            this.get('itemSize'),
            this.get('offset'),
            this.convertBoolModelToThree(this.get('normalized'), 'normalized')
        );
        return Promise.resolve(result);

    },

    createPropertiesArrays: function() {

        ThreeModel.prototype.createPropertiesArrays.call(this);
        this.three_properties.push('data');


        this.property_converters['data'] = 'convertThreeType';
        this.property_converters['itemSize'] = null;
        this.property_converters['offset'] = null;
        this.property_converters['normalized'] = 'convertBool';


    },

}, {

    model_name: 'InterleavedBufferAttributeModel',

    serializers: _.extend({
        data: { deserialize: widgets.unpack_models },
    },  ThreeModel.serializers),
});

module.exports = {
    InterleavedBufferAttributeModel: InterleavedBufferAttributeModel,
};
