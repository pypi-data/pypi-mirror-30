#include "common.hpp"
#include "key.hpp"

Key::Key(RCObj *pctx, HCRYPTKEY hk) throw(CSPException) {
    parent = pctx;
    parent->ref();
    hkey = hk;
    LOG("Key()\n");
}

Key::~Key() throw(CSPException) {
    LOG("release key\n");
    if (hkey) {
        bool res = CryptDestroyKey(hkey);
        if (!res) {
            throw CSPException("~Key:Couldn't destroy key");
        }
    }
    parent->unref();
}

void Key::encode(BYTE **s, DWORD *slen, Key *cryptkey) throw(CSPException) {
    LOG("Key::encode(%p)\n", cryptkey);
    HCRYPTKEY expkey;
    DWORD blobtype;
    if (cryptkey) {
        expkey = cryptkey -> hkey;
        blobtype = SIMPLEBLOB;
    } else {
        expkey = 0;
        blobtype = PUBLICKEYBLOB;
    }

    if(!CryptExportKey( hkey, expkey, blobtype, 0, NULL, slen)) {
        throw CSPException("Key::encode: Error computing key blob length");
    }

    *s = (BYTE *)malloc(*slen);

    if(!CryptExportKey( hkey, expkey, blobtype, 0, (BYTE *)*s, slen)) {
        free((void *)*s);
        throw CSPException("Key::encode: Error exporting key blob");
    }
};

void Key::store_cert(Cert *c) throw (CSPException) {
    if (!c || !c->pcert) {
        throw CSPException("Key.store_cert: invalid certificate");
    }
    if (!CryptSetKeyParam(hkey, KP_CERTIFICATE, (const BYTE*) c->pcert->pbCertEncoded, 0)) {
        throw CSPException("Key.store_cert: couldn't set key parameter");
    }
}

void Key::set_alg_id(ALG_ID id) throw (CSPException) {
    if (!CryptSetKeyParam(hkey, KP_ALGID, (LPBYTE) &id, 0)) {
        throw CSPException("Key.set_alg_id: couldn't set key parameter");
    }
}

void Key::set_iv(BYTE *STRING, DWORD LENGTH) throw (CSPException) {
    if (!CryptSetKeyParam(hkey, KP_IV, STRING, 0)) {
        throw CSPException("Key.set_iv: couldn't set key parameter");
    }
}

void Key::set_padding(DWORD padding) throw (CSPException) {
    if (!CryptSetKeyParam(hkey, KP_PADDING, (BYTE *)&padding, 0)) {
        throw CSPException("Key.set_padding: couldn't set key parameter");
    }
}

void Key::set_mode(DWORD mode) throw (CSPException) {
    if (!CryptSetKeyParam(hkey, KP_MODE, (LPBYTE) &mode, 0)) {
        throw CSPException("Key.set_mode: couldn't set key parameter");
    }
}

ALG_ID Key::alg_id() throw (CSPException) {
    ALG_ID res;
    DWORD size = sizeof(res);
    if(!CryptGetKeyParam(hkey, KP_ALGID, (BYTE*)&res, &size, 0))
    {
        DWORD err = GetLastError();
        throw CSPException("Key.alg_id: couldn't get key algorithm ID", err);
    }
    return res;
}

void Key::get_iv(BYTE **s, DWORD *slen) throw (CSPException) {
    if(!CryptGetKeyParam( hkey, KP_IV, NULL, slen, 0))
    {
        DWORD err = GetLastError();
        throw CSPException("Key::get_iv: couldn't get iv blob length", err);
    }
    *s = (BYTE*)malloc(*slen);
    if(!*s) {
        throw CSPException("Key::get_iv: memory allocation error");
    }
    if(!CryptGetKeyParam( hkey, KP_IV, *s, slen, 0))
    {
        DWORD err = GetLastError();
        throw CSPException("Key::get_iv: couldn't copy iv blob", err);
    }
}


void Key::extract_cert(BYTE **s, DWORD *slen) throw (CSPException) {
    if(!CryptGetKeyParam( 
        hkey, 
        KP_CERTIFICATE, 
        NULL, 
        slen, 
        0))
    {
        DWORD err = GetLastError();
        throw CSPException("Key::extract_cert: couldn't get certificate blob length", err);
    }

    *s = (BYTE*)malloc(*slen);

    if(!*s) {
        throw CSPException("Key::extract_cert: memory allocation error");
    }

    //--------------------------------------------------------------------
    // Копирование параметров ключа в BLOB.

    if(!CryptGetKeyParam( 
        hkey, 
        KP_CERTIFICATE, 
        *s, 
        slen, 
        0))
    {
        DWORD err = GetLastError();
        throw CSPException("Key::extract_cert: couldn't copy certificate blob", err);
    }
}


void Key::encrypt(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen) throw(CSPException)
{
    LOG("Key::encrypt(%p, %u)\n", STRING, LENGTH);
    LOG("    getting encrypted data size\n");
    // Вызов функции CryptEncryptMessage.
    *slen = LENGTH;
    // TODO: неизбыточное вычисление размера буфера
//     if(!CryptEncrypt( hkey, NULL, true, 0, NULL, slen, LENGTH)) {
//         DWORD err = GetLastError();
//         LOG("    error getting encrypted data size %x\n", err);
//         throw CSPException("Key::encrypt: Getting buffer size failed.", err);
//     }
    LOG("    encrypted data size is %u\n", *slen);
    // Распределение памяти под возвращаемый BLOB.
    *s = (BYTE*)malloc(LENGTH + 32768);
    if(!*s) {
        DWORD err = GetLastError();
        throw CSPException("Key::encrypt: Memory allocation error while encrypting.", err);
    }
    memcpy(*s, STRING, LENGTH);
    LOG("    encrypting data\n");
    // Повторный вызов функции CryptEncryptMessage для зашифрования содержимого.
    if(!CryptEncrypt( hkey, NULL, true, 0, *s, slen, LENGTH + 32768)) {
        DWORD err = GetLastError();
        LOG("    encryption error %x\n", err);
        free((void *)*s);
        throw CSPException("Key::encrypt: Encryption failed.", err);
    }
    LOG("    encrypted succesfully\n");
}

void Key::decrypt(BYTE *STRING, DWORD LENGTH, BYTE **s, DWORD *slen) throw(CSPException)
{
    LOG("Key::decrypt(%p, %u)\n", STRING, LENGTH);
    // Распределение памяти под возвращаемый BLOB.
    *slen = LENGTH;
    *s = (BYTE*)malloc(*slen);
    if(!*s) {
        DWORD err = GetLastError();
        throw CSPException("Key::decrypt: Memory allocation error while decrypting.", err);
    }
    memcpy(*s, STRING, LENGTH);
    LOG("    decrypting data\n");
    if(!CryptDecrypt( hkey, NULL, true, 0, *s, slen)) {
        DWORD err = GetLastError();
        LOG("    decryption error %x\n", err);
        free((void *)*s);
        throw CSPException("Key::decrypt: Decryption failed.", err);
    }
    *s = (BYTE *)realloc((void *)*s, (size_t)*slen) // новый размер данных может быть меньше исходного
    LOG("    decrypted succesfully\n");
}
