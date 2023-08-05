#include "Parser.h"

#include <iostream>

#include <clang-c/Index.h>

namespace {
    class String {
    public:
        String(CXString s): m_str(clang_getCString(s)), m_data(s) {}
        ~String() { clang_disposeString(m_data); }
        
        String(const String&) = delete;
        String(String&&) = delete;

        String& operator=(const String&) = delete;        
        String& operator=(String&) = delete;

        std::string str() { return m_str; }
    private:
        const char *m_str;
        CXString m_data;
    };

    class SourceLocation {
    public:
        SourceLocation(CXSourceLocation loc) {
            clang_getSpellingLocation(
                loc,
                &m_file,
                &m_line,
                nullptr,
                nullptr        
            );
        }

        std::string filename() { 
            String name(clang_getFileName(m_file));
            return name.str();      
        }

        unsigned lineno() { return m_line; } 

    private:
        CXFile m_file;
        unsigned m_line;
    };

    bool process_child(const CXCursor& cursor, const CXClientData& ctx) {
        auto cb = reinterpret_cast<Parser::Callback *>(ctx);
        auto callback = *cb;

        String name(clang_getCursorSpelling(cursor));
        SourceLocation loc = clang_getCursorLocation(cursor); 
        
        bool res = callback(
            name.str(),
            SymbolType::Function,
            loc.filename(),
            loc.lineno()
        );
        
        return res;
    }

    CXChildVisitResult visit(CXCursor child, CXCursor, CXClientData ctx) {
        if (!ctx)
            return CXChildVisit_Break;
        
        auto type = clang_getCursorType(child);
        switch (type.kind)
        {
            case CXType_FunctionProto:
            case CXType_FunctionNoProto:
                if (process_child(child, ctx))
                    return CXChildVisit_Continue;
                else
                    return CXChildVisit_Break;            
            default:
                return CXChildVisit_Recurse;
        }
    }
}

class ParserImpl {
public:
    ParserImpl() {
        m_index = clang_createIndex(1 , 0);
    }

    ~ParserImpl() {
        clang_disposeIndex(m_index);
    }

    void parse_file(
            const std::string& file,
            Parser::Callback cb) {
        CXTranslationUnit tu = clang_parseTranslationUnit(
            m_index,
            file.c_str(),
            nullptr,
            0,
            nullptr,
            0,
            CXTranslationUnit_SkipFunctionBodies
        );

        if (!tu)
            return;

        CXCursor cursor = clang_getTranslationUnitCursor(tu);
        clang_visitChildren(
            cursor,
            &visit,
            &cb 
        );

        clang_disposeTranslationUnit(tu);
    }

private:
    CXIndex m_index;
};

Parser::Parser(): m_impl(new ParserImpl()) {
}

Parser::~Parser() {
}

void Parser::parse_file(
        const std::string& file, 
        Callback cb) {
    m_impl->parse_file(file, cb);
}
