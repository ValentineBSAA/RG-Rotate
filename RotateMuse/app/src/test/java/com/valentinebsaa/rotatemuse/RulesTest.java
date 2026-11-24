package com.valentinebsaa.rotatemuse;
import org.junit.Test;
import static org.junit.Assert.*;
import java.util.TimeZone;
public class RulesTest {
 @Test public void twelveHourDefault(){assertEquals("12:00 AM",Rules.clock(0,false,false,TimeZone.getTimeZone("UTC")));}
 @Test public void twentyFourWithSeconds(){assertEquals("00:00:01",Rules.clock(1000,true,true,TimeZone.getTimeZone("UTC")));}
 @Test public void timezoneMatters(){assertEquals("17:00",Rules.clock(0,true,false,TimeZone.getTimeZone("GMT-07:00")));}
 @Test public void draggingStaysOnScreen(){assertEquals(0,Rules.clamp(-2),0);assertEquals(1,Rules.clamp(2),0);assertEquals(.5f,Rules.clamp(Float.NaN),0);}
 @Test public void sleepBoundary(){assertFalse(Rules.expired(119999,2));assertTrue(Rules.expired(120000,2));assertFalse(Rules.expired(Long.MAX_VALUE,0));}
 @Test public void acceptsOnlyLocalMediaTypes(){assertTrue(Rules.mediaType("video/mp4"));assertTrue(Rules.mediaType("image/gif"));assertFalse(Rules.mediaType("text/html"));assertFalse(Rules.mediaType(null));}
}
