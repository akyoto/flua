#!/bin/sh
cat LangBPC.hpp | grep if\(exprLeft | sed -s 's/.*if(exprLeft == "\([^"]*\)".*/\1/' > keywords.txt
