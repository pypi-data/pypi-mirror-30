C FUNCTION ISTRLN (STRING)  Returns index of last non-blank
C                           character.  Returns zero if string is
C                           null or all blank.

      FUNCTION ISTRLN (STRING)
      CHARACTER*(*)  STRING
      CHARACTER BLANK, TAB
      PARAMETER (BLANK = ' ', TAB = '	')
C     there is a tab character here  ^

C  -- If null string or blank string, return length zero.
      ISTRLN = 0
      IF (STRING (1:1) .EQ. CHAR(0))  RETURN
      IF (STRING .EQ. ' ')  RETURN

C  -- Find rightmost non-blank character.
      ILEN = LEN (STRING)
      DO 20  I = ILEN, 1, -1
         IF (STRING(I:I).NE.BLANK .AND. STRING(I:I).NE.TAB
     &        .AND. STRING(I:I).NE.CHAR(0))  GOTO 30
   20 CONTINUE
   30 ISTRLN = I

      RETURN
      END
C SUBROUTINE TRIML (STRING)  Removes leading blanks.

      SUBROUTINE TRIML (STRING)
      CHARACTER*(*)  STRING
      CHARACTER*200  TMP
      CHARACTER BLANK, TAB
      PARAMETER (BLANK = ' ', TAB = '	')
C     there is a tab character here  ^

      JLEN = ISTRLN (STRING)

C  -- All blank and null strings are special cases.
      IF (JLEN .EQ. 0)  RETURN

C  -- FInd first non-blank char
      DO 10  I = 1, JLEN
         IF (STRING(I:I).NE.BLANK .AND. STRING(I:I).NE.TAB)  GOTO 20
   10 CONTINUE
   20 CONTINUE

C  -- If I is greater than JLEN, no non-blanks were found.
      IF (I .GT. JLEN)  RETURN

C  -- Remove the leading blanks.
      TMP = STRING (I:)
      STRING = TMP
      RETURN
      END
C SUBROUTINE UPPER (STRING)  Changes a-z to upper case.

      SUBROUTINE UPPER (STRING)
      CHARACTER*(*)  STRING

      JLEN = ISTRLN (STRING)

      DO 10  I = 1, JLEN
         IC = ICHAR (STRING (I:I))
         IF ((IC .LT. 97)  .OR.  (IC .GT. 122))  GOTO 10
         STRING (I:I) = CHAR (IC - 32)
   10 CONTINUE

      RETURN
      END
C SUBROUTINE LOWER (STRING)  Changes A-Z to lower case.

      SUBROUTINE LOWER (STRING)
      CHARACTER*(*)  STRING

      JLEN = ISTRLN (STRING)

      DO 10  I = 1, JLEN
         IC = ICHAR (STRING (I:I))
         IF ((IC .LT. 65) .OR.  (IC .GT. 90))  GOTO 10
         STRING (I:I) = CHAR (IC + 32)
   10 CONTINUE

      RETURN
      END
C***********************************************************************
C
      SUBROUTINE BWORDS (S, NWORDS, WORDS)
C
C     Breaks string into words.  Words are seperated by one or more
C     blanks or tabs, or a comma and zero or more blanks.
C
C     ARGS        I/O      DESCRIPTION
C     ----        ---      -----------
C     S            I       CHAR*(*)  String to be broken up
C     NWORDS      I/O      Input:  Maximum number of words to get
C                          Output: Number of words found
C     WORDS(NWORDS) O      CHAR*(*) WORDS(NWORDS)
C                          Contains words found.  WORDS(J), where J is
C                          greater then NWORDS found, are undefined on
C                          output.
C
C      Written by:  Steven Zabinsky, September 1984
C      Tab char added July 1994.
C
C**************************  Deo Soli Gloria  **************************

C  -- No floating point numbers in this routine.
      IMPLICIT INTEGER (A-Z)

      CHARACTER*(*) S, WORDS(NWORDS)

      CHARACTER BLANK, COMMA, TAB
      PARAMETER (BLANK = ' ', COMMA = ',', TAB = '	')
C     there is a tab character here               ^.

C  -- BETW    .TRUE. if between words
C     COMFND  .TRUE. if between words and a comma has already been found
      LOGICAL BETW, COMFND

C  -- Maximum number of words allowed
      WORDSX = NWORDS

C  -- SLEN is last non-blank character in string
      SLEN = ISTRLN (S)

C  -- All blank string is special case
      IF (SLEN .EQ. 0)  THEN
         NWORDS = 0
         RETURN
      ENDIF

C  -- BEGC is beginning character of a word
      BEGC = 1
      NWORDS = 0

      BETW   = .TRUE.
      COMFND = .TRUE.

      DO 10  I = 1, SLEN
         IF (S(I:I) .EQ. BLANK .OR. S(I:I) .EQ. TAB)  THEN
            IF (.NOT. BETW)  THEN
               NWORDS = NWORDS + 1
               WORDS (NWORDS) = S (BEGC : I-1)
               BETW = .TRUE.
               COMFND = .FALSE.
            ENDIF
         ELSEIF (S(I:I) .EQ. COMMA)  THEN
            IF (.NOT. BETW)  THEN
               NWORDS = NWORDS + 1
               WORDS (NWORDS) = S(BEGC : I-1)
               BETW = .TRUE.
            ELSEIF (COMFND)  THEN
               NWORDS = NWORDS + 1
               WORDS (NWORDS) = BLANK
            ENDIF
            COMFND = .TRUE.
         ELSE
            IF (BETW)  THEN
               BETW = .FALSE.
               BEGC = I
            ENDIF
         ENDIF

         IF (NWORDS .GE. WORDSX)  RETURN

   10 CONTINUE

      IF (.NOT. BETW  .AND.  NWORDS .LT. WORDSX)  THEN
         NWORDS = NWORDS + 1
         WORDS (NWORDS) = S (BEGC :SLEN)
      ENDIF

      RETURN
      END
      SUBROUTINE UNTAB (STRING)
C REPLACE TABS WITH BLANKS :    TAB IS ASCII DEPENDENT
      INTEGER        ITAB , I, ILEN, ISTRLN
      PARAMETER      (ITAB = 9)
      CHARACTER*(*)  STRING, TAB*1
      EXTERNAL ISTRLN
      TAB  = CHAR(ITAB)
      ILEN = MAX(1, ISTRLN(STRING))
 10   CONTINUE
        I = INDEX(STRING(:ILEN), TAB )
        IF (I .NE. 0) THEN
            STRING(I:I) = ' '
            GO TO 10
        END IF
      RETURN
C END SUBROUTINE UNTAB
      END

      logical function iscomm (line)
c     returns true if line is a comment or blank line, false otherwise
      character*(*) line
      iscomm = ((line.eq.' ').or.(index(';*%#',line(1:1)).ne.0))
      return
      end

      subroutine str2dp(str, dpval, ierr)
c  return dp number "dpval" from character string "str"
c  if str cannot be a number, ierr < 0 is returned.
      character*(*) str, fmt*15
      double precision dpval
      integer  ierr
      logical  isnum
      external isnum
      ierr = -999
      if (isnum(str)) then
         ierr = 0
         write(fmt, 10) min(999,max(2,len(str)))
 10      format('(bn,f',i3,'.0)')
         read(str, fmt, err = 20, iostat=ierr) dpval
      end if
      if (ierr.gt.0) ierr = -ierr
      return
 20   continue
      ierr = -998
      return
c end subroutine str2dp
      end

             logical function isnum (string)
c  tests whether a string can be a number. not foolproof!
c  to return true, string must contain:
c    - only characters in  'deDE.+-, 1234567890' (case is checked)
c    - no more than one 'd' or 'e'
c    - no more than one '.'
c    - if '+' or '-' is seen after a digit, 'deDE' must be seen.
c  matt newville
       character*(*)  string,  number*20
c note:  layout and case of *number* is important: do not change!
       parameter (number = 'deDE.,+- 1234567890')
       integer   iexp, idec, i, j, istrln, isign
       integer   jexp
       logical   ldig, l_op
       external  istrln
c       str   = string
c       call triml(str)
       iexp  = 0
       jexp  = 0
       idec  = 0
       isign = 0
       ldig  = .false.
       l_op  = .false.
       isnum = .false.
       do 100  i = 1, max(1, istrln(string))
          j = index(number,string(i:i))
cc          print*, 'X  ' , i, j, ' : ' , str(i:i)
          if (j.le.0)               go to 200
          if (j.ge.10)              ldig = .true.
          if((j.ge.1).and.(j.le.4)) then
             iexp = iexp + 1
             jexp = i
          endif
          if (j.eq.5)               idec = idec + 1
          if ((j.eq.7).or.(j.eq.8)) then
             isign= isign +1
             if ((i .gt. 1) .and. (i .ne. (jexp+1))) then
                l_op = .true.
             endif
          endif
 100   continue
c  every character in "string" is also in "number".  so, if there are
c  not more than one exponential and decimal markers, it's a number
       if ((iexp.le.1).and.(idec .le.1)) isnum = .true.
       if ((iexp.eq.0).and.(isign.gt.1)) isnum = .false.
       if (jexp.eq.1)  isnum = .false.
       isnum = isnum .and. (.not.l_op)
cc       print*, 'ISNUM: ', string(1:istrln(string))
cc       print*, '       ', isnum, l_op, iexp, idec, isign
 200   continue
       return
c  end logical function isnum
       end
