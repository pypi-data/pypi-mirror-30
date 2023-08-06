# Copyright (c) 2004-2010 Business Management Systems. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the same terms as Python itself.
#
import unittest
from . import ses
import time

class SESTestCase(unittest.TestCase):

  def setUp(self):
    self.ses = ses.SES('shhh!')

  def testEncode(self):
    for bits in (0,1,1234,123738493059846347859040389523479):
      s = self.ses.encode(bits)
      self.assertEqual(bits,self.ses.decode(s))

  def testTimecode(self):
    tc = self.ses.get_timecode()
    for tc in (0,1,50000,60000,tc):
      secs = self.ses.timecode_as_secs(tc)
      self.assertEqual(tc,self.ses.get_timecode(secs))

  def testHash(self):
    data = (b'now', b'is', b'the', b'time')
    h = self.ses.hash_create(*data)
    self.assertTrue(self.ses.hash_verify(h,*data))
    self.assertTrue(not self.ses.hash_verify(h, b'some', b'other', b'data'))

  def testMessageID(self):
    while True:
      tc,msgid = self.ses.create_message_id()
      tc2,msgid2 = self.ses.create_message_id()
      if tc2 == tc: break
    # message ID increments when timecode is unchanged
    self.assertEqual(msgid+1,msgid2)
    # message ID resets when timecode changes
    self.ses.last_ts -= 1
    tc2,msgid2 = self.ses.create_message_id()
    self.assertEqual(tc,tc2)
    self.assertEqual(1,msgid2)

  def testSigpack(self):
    tc = 50000
    h = self.ses.hash_create(b'some',b'data')
    for msgid in (1,100000,12345657423784):
      sig = self.ses.sig_create(msgid,tc,h)
      ts = tc + 30
      msgid2,tc2,h2 = self.ses.sig_extract(sig,ts)
      self.assertTrue(tc2 <= ts)
      self.assertEqual(msgid,msgid2)
      self.assertEqual(tc,tc2)
      self.assertEqual(h,h2)
      ts = tc + 200
      msgid2,tc2,h2 = self.ses.sig_extract(sig,ts)
      self.assertTrue(tc2 <= ts)
      self.assertEqual(msgid,msgid2)
      self.assertNotEqual(tc,tc2)
      self.assertEqual(h,h2)

  def get_timecode(self):
    "Provide a deterministic timecode for testing."
    return self.timecode

  def testSign(self):
    self.ses.get_timecode = self.get_timecode
    self.timecode = 60000
    a = 'mickey@Mouse.com'
    sig = self.ses.sign(a)
    self.assertTrue(sig.endswith(a))
    self.assertTrue(sig.startswith('SES='))
    res = self.ses.verify(sig)
    self.assertEqual(res,(a,self.timecode,self.ses.last_id))
    res2 = self.ses.verify(sig.lower())
    self.assertEqual(res2,(a.lower(),res[1],res[2]))

  def testValtrack(self):
    a = 'mickey@Mouse.com'
    sig = self.ses.sign(a)
    res = self.ses.verify(sig)
    res = self.ses.verify(sig)
    res = self.ses.verify(sig)
    try:
      res = self.ses.verify(sig)
      self.fail("Failed to limit validations")
    except:
      pass

  def testFixed(self):
    self.ses.get_timecode = self.get_timecode
    self.timecode = 60000
    a = 'mickey@Mouse.com'
    # sigs are normaly always unique 
    sig = self.ses.sign(a)
    sig2 = self.ses.sign(a)
    self.assertNotEqual(sig,sig2)
    # but passing a msgid generates a fixed sig
    msgid = 12345678
    sig = self.ses.sign(a,msgid)
    sig2 = self.ses.sign(a,msgid)
    self.assertEqual(sig,sig2)
    # that is unchanging with time as well
    self.timecode = 70000
    sig = self.ses.sign(a,msgid)
    self.assertEqual(sig,sig2)
    a2,tc,msgid2 = self.ses.verify(sig)
    self.assertEqual(a2,a)
    self.assertEqual(tc,0)
    self.assertEqual(msgid2,msgid)

if __name__ == '__main__':
  unittest.main()
