      program test_pad

      integer npack, nwords, ierr
      double precision f1, f2, unpad
      external unpad
      character*8  s1
      character*100 line
      character*60 words(16)

      open (unit=1, file='pad_test.dat', status='old')

 90   format(a)

 100  continue
      read(1, 90, end=300) line
      call triml(line)
      nwords = 8
      npack = 8
      call bwords(line, nwords, words)
      do 200 i = 1, nwords
         call str2dp(words(i), f1,  ierr)
         call pad(f1, npack, s1)
         f2 = unpad(s1, npack)
         print 299, ' ', s1, ' : ', f1, ' : ', f2
 200  continue
      goto 100
 300  continue
 299  format(3a, g24.13, a, g24.13)
      end
