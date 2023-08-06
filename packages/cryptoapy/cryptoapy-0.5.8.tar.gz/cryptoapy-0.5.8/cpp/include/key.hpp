#ifndef KEY_HPP_INCLUDED
#define KEY_HPP_INCLUDED

#include "context.hpp"
#include "except.hpp"
#include "cert.hpp"
#include "rcobj.hpp"

class Hash;
class Key : public RCObj
{
    HCRYPTKEY hkey;
    RCObj *parent;
public:
    Key(RCObj *pctx, HCRYPTKEY hk) throw(CSPException);

    ~Key() throw(CSPException);

    void encode(BYTE **s, DWORD *slen, Key *cryptkey=NULL) throw(CSPException);

    void store_cert(Cert *c) throw (CSPException);

    void extract_cert(BYTE **s, DWORD *slen) throw (CSPException);

    void encrypt(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen) throw(CSPException);

    void decrypt(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen) throw(CSPException);

    void set_alg_id(ALG_ID id) throw (CSPException);
    void set_mode(DWORD mode) throw (CSPException);
    ALG_ID alg_id() throw (CSPException);
    void get_iv(BYTE **s, DWORD *slen) throw (CSPException);
    void set_iv(BYTE *STRING, DWORD LENGTH) throw (CSPException);
    void set_padding(DWORD padding) throw (CSPException);

    friend class Crypt;
    friend class Hash;
};

#endif
