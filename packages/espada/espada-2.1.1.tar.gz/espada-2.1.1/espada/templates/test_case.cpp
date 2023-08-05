// {{f_name}}_tests.{{ext}} create by {{user_name}} on {{date_time}}
#include "catch.hpp"
#include "fakeit.hpp"
#include <{{f_name}}.h>

// tutorial: https://github.com/philsquared/Catch/blob/master/docs/tutorial.md
// API Reference: https://github.com/philsquared/Catch/blob/master/docs/Readme.md
// FakeIt: https://github.com/eranpeer/FakeIt/wiki/Quickstart

{{class_name}} target;
TEST_CASE("Define what you are testing", "[{{class_name}}]"){

    REQUIRE(true);
}

