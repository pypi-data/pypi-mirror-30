/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                               PUBLIQUIZ SCHEMA
// ****************************************************************************

if (!$.publiquiz) $.publiquiz = {};

$.publiquiz.schemaEngine = [
    "choices-radio", "choices-check", "blanks-fill", "blanks-select",
    "blanks-media","blanks-choices","correct-line", "pointing",
    "pointing-categories", "matching", "sort", "categories", "wordsearch",
    "flashcard", "coloring", "memory", "production"];

$.publiquiz.schemaBlockBlanks = [
    "blanks.p", "blanks.list", "blanks.blockquote", "blanks.speech",
    "table", "media"];

$.publiquiz.schemaBlockBlanksChoices = [
    "blanks-c.p", "blanks-c.list", "blanks-c.blockquote", "blanks-c.speech",
    "table", "media"];

$.publiquiz.schemaBlockCorrect = [
    "correct.p", "correct.list", "correct.blockquote", "correct.speech",
    "table", "media"];
$.publiquiz.schemaBlockPointing = [
    "pointing.p", "pointing.list", "pointing.blockquote", "pointing.speech",
    "table", "media"];

$.publiquiz.schemaInlineBlanks = $.publidoc.schemaInline.concat(["blank"]);
$.publiquiz.schemaInlineBlanksChoices = $.publidoc.schemaInline.concat(["blanks-c.blank"]);

$.publiquiz.schemaInlineCorrect = $.publidoc.schemaInline.concat(["char"]);
$.publiquiz.schemaInlinePointing = $.publidoc.schemaInline.concat(["point"]);

$.publiquiz.schema = $.extend(
    {}, $.publidoc.schema,
    {
        // ------ DIVISION ----------------------------------------------------
        ".division": {
            content: [["division", "topic", "quiz"]]
        },
        division: {
            attributes: { type: null, "xml:lang": $.publidoc.schemaAttLang },
            content: [["division.head", "division", "topic", "quiz"]]
        },

        // ------ COMPONENT ---------------------------------------------------
        quiz: {
            attributes: {
                id: null,
                type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["component.head", "instructions", "composite", "help",
                       "answer"].concat($.publiquiz.schemaEngine)]
        },

        // ------ SECTION -----------------------------------------------------
        ".instructions": {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },
        instructions: {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },

        "blanks.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "blanks.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockBlanks)],
            seed: "<section><p e4x='here'/></section>"
        },
        "blanks-c.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "blanks.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockBlanksChoices)],
            seed: "<section><p e4x='here'/></section>"
        },
        "correct.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "correct.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockCorrect)],
            seed: "<section><p e4x='here'/></section>"
        },
        "pointing.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "pointing.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockPointing)],
            seed: "<section><p e4x='here'/></section>"
        },

        ".help": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        help: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        ".answer": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        answer: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },

        // ------ SECTION - Choices -------------------------------------------
        "choices-radio": {
            type: "radio",
            rightElement: "right",
            wrongElement: "wrong",
            attributes: { shuffle: ["true", "false"] },
            content: [["right", "wrong"]]
        },
        "choices-check": {
            type: "checkbox",
            rightElement: "right",
            wrongElement: "wrong",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                shuffle: ["true", "false"] },
            content: [["right", "wrong"]]
        },
        right: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },
        wrong: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },

        // ------ SECTION - Blanks --------------------------------------------
        "blanks-fill": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                strict: ["true", "false"], long: null },
            content: [["blanks.section"], $.publiquiz.schemaBlockBlanks]
        },

        "blanks-select": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"], "no-shuffle": ["true", "false", "alpha"],
                orientation: ["east", "west", "south"] },
            content: [["blanks.intruders", "blanks.section"],
                      ["blanks.intruders"].concat(
                          $.publiquiz.schemaBlockBlanks)]
        },

        "blanks-media": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"], "no-shuffle": ["true", "false", "alpha"] },
            content: [["blanks.intruders", "blanks.section"],
                      ["blanks.intruders"].concat(
                          $.publiquiz.schemaBlockBlanks)]
        },

        "blanks-choices": {
            content: [["blanks-c.section"], $.publiquiz.schemaBlockBlanksChoices]
        },

        "blanks.intruders": {
            element: "intruders",
            content: [["blank"]]
        },

        // ------ SECTION - Correct-line --------------------------------------
        "correct-line": {
            attributes: {
                "remove-space": ["true", "false"] },
            content: [["correct.intruders", "correct.section"],
                      ["correct.intruders"].concat(
                          $.publiquiz.schemaBlockCorrect)]
        },
        "correct.intruders": {
            element: "intruders",
            content: [["char"]]
        },

        // ------ SECTION - Pointing ------------------------------------------
        pointing: {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                type: ["radio", "check"] },
            content: [["pointing.section"],
                      $.publiquiz.schemaBlockPointing]
        },
        "pointing-categories": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"] },
            content: [["pointing-c.categories", "pointing.section"]]
        },
        "pointing-c.categories": {
            element: "categories",
            content: [["pointing-c.category"]]
        },
        "pointing-c.category": {
            element: "category",
            attributes: { id: ["1", "2", "3", "4", "5"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Matching ------------------------------------------
        matching: {
            intrudersElement: "intruders",
            matchElement: "match",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"],
                orientation: ["east", "west", "south"] },
            content: [["matching.intruders", "match"]]
        },
        "matching.intruders": {
            element: "intruders",
            content: [["match.item"]]
        },
        match: {
            content: [["match.item"]]
        },
        "match.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Sort ----------------------------------------------
        sort: {
            comparisonElement: "comparison",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                shuffle: ["true", "false"],
                orientation: ["east", "west", "south"] },
            content: [["comparison", "sort.item"]]
        },
        comparison: {
            content: [[".text"]]
        },
        "sort.item": {
            element: "item",
            attributes: {
                shuffle: ["1", "2", "3", "4", "5", "6", "7", "8", "9",
                          "10", "11", "12", "13", "14", "15"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Categories ----------------------------------------
        categories: {
            intrudersElement: "intruders",
            categoryElement: "category",
            headElement: "head",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"], "no-shuffle": ["true", "false", "alpha"],
                orientation: ["east", "west", "south"] },
            content: [["category.intruders", "category"]]
        },
        "category.intruders": {
            element: "intruders",
            content: [["category.item"]]
        },
        category: {
            content: [["category.head", "category.item"]]
        },
        "category.head": {
            element: "head",
            content: [["title", "shorttitle", "subtitle"]]
        },
        "category.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Production ----------------------------------------
        ".production": {
            content: [[".text"]]
        },
        production: {
            content: [[".text"]]
        },

        // ------ SECTION - Wordsearch ----------------------------------------
        wordsearch: {
            content: [["words", "grid"]]
        },
        words: {
            content: [["words.item"]]
        },
        "words.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },
        grid: {
            content: [["grid.line"]]
        },
        "grid.line": {
            element: "line",
            content: [["grid.cell"]]
        },
        "grid.cell": {
            element: "cell",
            content: [[".text"]]
        },

        // ------ SECTION - Flashcard -----------------------------------------
        flashcard: {
            content: [["side1", "side2"]]
        },

        side1: {
            content: [["section"], $.publidoc.schemaBlock]
        },

        side2: {
            content: [["instructions", "help", "answer"]
                      .concat($.publiquiz.schemaEngine)]
        },

        // ------ SECTION - Coloring --------------------------------------------
        coloring: {
            attributes: { nomark: ["true", "false"] },
            content: [["palette", "canvas", "areas"]]
        },
        palette: {
            content: [["color"]]
        },
        canvas: {
            attributes: { id: null }
        },
        areas: {
            attributes: { id: null }
        },
        color: {
            attributes: { code: null, codeRef: null }
        },

        // ------ SECTION - Memory ----------------------------------------------
        memory: {
            matchElement: "match",
            itemElement: "item",
            attributes: {
                display : null,
                delay : null},
            content: [["mmatch"]]
        },
        "memory.match": {
            element: "match",
            content: [["memory-m.item"]]
        },
        "memory-m.item": {
            element: "item",
            content: [["image"]]
        },

        // ------ SECTION - Composite -----------------------------------------
        composite: {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multipage: ["true", "false"] },
            content: [["subquiz"]]
        },
        subquiz: {
            content: [["instructions", "help", "answer"]
                      .concat($.publiquiz.schemaEngine)]
        },

        // ------ BLOCK -------------------------------------------------------
        "blanks.p": {
            element: "p",
            content: [$.publiquiz.schemaInlineBlanks]
        },
        "blanks-c.p": {
            element: "p",
            content: [$.publiquiz.schemaInlineBlanksChoices]
        },
        "correct.p": {
            element: "p",
            content: [$.publiquiz.schemaInlineCorrect]
        },
        "pointing.p": {
            element: "p",
            content: [$.publiquiz.schemaInlinePointing]
        },

        "blanks.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "blanks.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "blanks-c.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "blanks-c.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "correct.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "correct.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "pointing.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "pointing.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "blanks.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockBlanks),
                      $.publiquiz.schemaInlineBlanks]
        },
        "blanks-c.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockBlanksChoices),
                      $.publiquiz.schemaInlineBlanksChoices]
        },
        "correct.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockCorrect),
                      $.publiquiz.schemaInlineCorrect]
        },
        "pointing.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockPointing),
                      $.publiquiz.schemaInlinePointing]
        },

        "blanks.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "blanks.p", "blanks.list",
                       "blanks.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },
        "blanks-c.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "blanks-c.p", "blanks-c.list",
                       "blanks-c.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },
        "correct.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "correct.p", "correct.list",
                       "correct.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },
        "pointing.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "pointing.p", "pointing.list",
                       "pointing.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },

        "blanks.speech": {
            element: "speech",
            content: [["speaker", "stage", "blanks.p",
                       "blanks.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },
        "blanks-c.speech": {
            element: "speech",
            content: [["speaker", "stage", "blanks-c.p",
                       "blanks-c.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },
        "correct.speech": {
            element: "speech",
            content: [["speaker", "stage", "correct.p",
                       "correct.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },
        "pointing.speech": {
            element: "speech",
            content: [["speaker", "stage", "pointing.p",
                       "pointing.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },

        // ------ INLINE ------------------------------------------------------
        blank: {
            content: [[".text"], ["s"]],
            attributes: {
                area: ["true", "false"],
                long: null }
        },

        s: {
            content: [[".text"]]
        },
        char: {
            content: [[".text"]],
            attributes: {
                function: ["uppercase", "accent"] }
        },
        point: {
            attributes: {
                ref: ["right", "cat1", "cat2", "cat3", "cat4", "cat5"] },
            content: [$.publidoc.schemaInline]
        },

        "blanks-c.blank": {
            element: "blank",
            attributes: {
                form: ["radio", "check"]
            },
            content: [["blanks-c.right", "blanks-c.wrong", "help", "answer"]],
            seed: "<blank><wrong e4x='here'/></blank>",
            seedRight: "<blank><right e4x='here'/></blank>"
        },

        "blanks-c.right": {
            element: "right",
            content: [$.publidoc.schemaInline]
        },
        "blanks-c.wrong": {
            element: "wrong",
            content: [$.publidoc.schemaInline]
        }

    }
);


})(jQuery);
