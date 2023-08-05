#ifndef __PARSER_H_
#define __PARSER_H_

#include <string>
#include <memory>
#include <functional>

class ParserImpl;

enum class SymbolType {
    Function,
    Variable,
    Class, 
};

class Parser {
public:
    
    using Callback = std::function<
        bool(
            const std::string&, // Symbol name
            SymbolType,         // Symbol type            
            const std::string&, // Filename
            unsigned            // Line number 
            )
        >;
public:
    Parser();
    ~Parser(); 
    
    /*
     * Parse a single translation unit, calling callback for every symbol.
     */ 
    void parse_file(const std::string& file, Callback cb);

private:
    std::unique_ptr<ParserImpl> m_impl;
};

#endif  //__PARSER_H_
