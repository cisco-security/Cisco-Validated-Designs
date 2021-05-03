module.exports = {
    'extends': "eslint:recommended",
    'parserOptions': {
        'ecmaVersion': 6,
    },

    'rules': {
        'no-unused-vars': "off",
        'no-undef': "off",

        // https://eslint.org/docs/rules/array-bracket-spacing
        'array-bracket-spacing': ['error', 'never'],

        // Use the one true brace style
        //'brace-style': ['error', '1tbs'],

        // Enforce using camelCase
        'camelcase': ['error', {'properties': 'always'}],

        // Indent at 4 spaces
        //'indent': ['error', 2],

        // No trailing spaces in code
        'no-trailing-spaces': ['error'],
    },
}
