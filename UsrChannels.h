#pragma once

// All directions in magnetic

// multiboat channels

enum ExChannels
{
	ExUtc,					// Microsoft DATE type,utc system time
	ExBsp,
	ExAwa,
	ExAws,
	ExTwa,
	ExTws,
	ExTwd,

	ExRudderFwd,
	ExDeltaTargBsp,
	ExCourse,
	
	ExLwy,
	ExSet,
	ExDrift,
	ExHdg,
	ExAirTemp,
	ExSeaTemp,
	ExBaro,
	ExDepth,				// metres
	ExRoll,
	ExPitch,
	ExRudder,
	ExTab,
	ExForestayLoad,
	ExDownhaulLoad,
	ExMastAngle,
	ExForestayLen,
	ExMast,
	ExStbdLoadCell,
	ExPortLoadCell,
	ExRake,
	ExVolts,
	ExVmg,
	ExROT,
	ExLayDistOnStrb,
	ExLayTimeOnStrb,
	ExLayPortBear,
	ExLayDistOnPort,
	ExLayTimeOnPort,
	ExLayStrbBear,
	ExGpsQuality,			// 0 Bad, 1 Autonomous, 2 Differential, 3 p-code, 4,5 Rtk, 6 dr, if change this, need to change CPort::NmeaAPB()
	ExGpsHDOP,
	ExGpsPDOP,
	ExGpsVDOP,
	ExGpsNumber,			// Number of satellites in active constellation
	ExGpsAge,				// Age of differential data
	ExGpsAltitude,			// antenna height
	ExGpsGeoidSeparation,
	ExGpsMode,				// 0 = 1D, 1 = 2D, 2 = 3D, 3 = Auto, 6 = error
	
	ExLat,					// if add GPS vars, extend CCore::IsGPSvar()
	ExLon,
	ExCog,
	ExSog,
	
	ExDiffRefStn,
	
	ExTargTwaN,
	ExTargBspN,
	ExTargVmg,
	ExTargRoll,
	ExPolarBsp,
	ExPolarBspPercent,
	ExPolarRoll,
	
	ExErrorCode,
	
	ExStrbRunner,
	ExPortRunner,

	ExPolarBspN,
	ExPolarBspPercentN,

	ExTargTwaLwy,			// target twa without leeway

	ExVmgPercent,
	
	ExVang,
	ExTraveller,
	ExMainSheet,
	
	ExPolVmcToMark,			// vmc if headed at mark
		
	ExKeelAngle,
	ExKeelHeight,
	ExBoard,
	ExEngineOilPressure,
	ExRPM1,
	ExRPM2,
	
	ExBoardP,
	ExBoardS,
	
	ExOppTrack,
	ExDistFinish,
	
	ExStartTimeToPort,
	ExStartTimeToStrb,
	ExLineSquareWind,
	ExStartDistToLine,
	ExStartRchTimeToLine,	// time to reach into line
	ExStartRchDistToLine,
	ExStartRchBspToLine,
	
	ExMarkTime,
	ExNextMarkTimeOnPort,
	ExNextMarkTimeOnStrb,
	
	ExXte,
	ExVmc,
	
	ExMagVar2,
	
	ExGwd,
	ExGws,
	
	ExLayDist,				// distance to layline we are heading to
	ExLayTime,				// time to layline
	ExLayBear,				// bearing of that layline
	
	ExVmcPercent,
	ExPolVmc,
	ExOptVmc,
	ExOptVmcHdg,
	ExOptVmcTwa,
	ExDeltaTargTwa,
	
	ExMarkRng,
	ExMarkBrg,
	ExMarkGpsTime,
	ExMarkTwa,
	
	ExPredSet,
	ExPredDrift,
	
	ExNextMarkRng,
	ExNextMarkBrg,
	ExNextMarkTwa,
	
	ExRadarRng,
	ExRadarBrg,
	ExStartDistBelowLineStern,
	
	ExAlt0,					// alternating number channels must be consecutive
	ExAlt1,
	ExAlt2,
	ExAlt3,
	ExAlt4,
	ExAlt5,
	ExAlt6,
	ExAlt7,
	ExAlt8,
	ExAlt9,
//	ExAltNum = ExAlt9 - ExAlt0 + 1	// defined in CoreMem.h
	ExAltMaxId = ExAlt9,			// alternating channels must be consecutive

	ExNextMarkPolTime,
	
	ExStartLineBiasDeg,
	ExStartLineBiasLen,
	
	ExStartLayPortBear,		// laylines for start line
	ExStartLayStrbBear,
	
	ExNextMarkAwa,
	ExNextMarkAws,
	
	ExStartRSTime,			// turning to right, ending up on starboard
	ExStartRPTime,			// turning to right, ending up on port
	ExStartLSTime,			// turning to left, ending up on starboard
	ExStartLPTime,			// turning to left, ending up on port
	
	ExGpsDistToRaceNote,
	ExGpsTimeToRaceNote,
	
	ExLogBsp,
	ExLogSog,
	ExStartGpsTimeToLine,
	ExStartGpsTimeToBurn,
	ExTargTwaS,				// Start
	ExTargBspS,				// Start
	
	ExGpsTime,
	
	ExTwdPlus90,			// Twd + 90
	ExTwdLess90,			// Twd - 90
	
	ExShadow,
	ExShadowOppTack,
	
	ExDownhaulLoad2,
	
	ExTackAngle,
	ExTackAnglePolar,
	
	ExTargAwa,
	
	ExStartTimeBurnPortX,	// offset for the start stbd layline to the pin
	ExStartTimeBurnStrbX,	// time to burn when tack onto starboard end starboard layline and sail to 20s from line
	ExStartLayTimeP,
	ExStartLayTimeS,

	ExMarkSet,
	ExMarkDrift,
	
	ExMarkLat,
	ExMarkLon,
	ExStartPortEndLat,		// ends of line
	ExStartPortEndLon,
	ExStartStrbEndLat,
	ExStartStrbEndLon,
	
	ExGpsHPE,
	ExHumidity,
	ExLeadPort,
	ExLeadStbd,
	ExBackstay,
	
	ExUser0,				// user channels must be consecutive
	ExUser1,
	ExUser2,
	ExUser3,
	ExUser4,
	ExUser5,
	ExUser6,
	ExUser7,
	ExUser8,
	ExUser9,
	ExUser10,
	ExUser11,
	ExUser12,
	ExUser13,
	ExUser14,
	ExUser15,
	ExUser16,
	ExUser17,
	ExUser18,
	ExUser19,
	ExUser20,
	ExUser21,
	ExUser22,
	ExUser23,
	ExUser24,
	ExUser25,
	ExUser26,
	ExUser27,
	ExUser28,
	ExUser29,
	ExUser30,
	ExUser31,
	ExUserNum = (ExUser31 - ExUser0 + 1),
	ExUserMax = ExUser31,		// user channels must be consecutive
	
	ExStartTimeToGun,
	ExStartTimeToLine,
	ExStartTimeToBurn,
	ExStartDistBelowLine,
	ExStartDistBelowLineGun,
	
	ExGateTimeOnPort,			// this is to the gate mark
	ExGateDistOnStrb,
	ExGateTimeOnStrb,
	ExGateDistOnPort,
	
	ExGateSpotTimeOnStrb,
	ExGateSpotTimeOnPort,
	
	ExLayPortBearUp,
	ExLayStrbBearUp,
	ExLayPortBearDn,
	ExLayStrbBearDn,
	
	ExTideLayPortTimeOnPort,
	ExTideLayPortTimeOnStbd,
	ExTideLayStbdTimeOnPort,
	ExTideLayStbdTimeOnStbd,
	ExTideLayPortTime,
	ExTideLayStbdTime,
	
	ExMaxLayPortBear,
	ExMinLayPortBear,
	ExMaxLayStrbBear,
	ExMinLayStrbBear,
	
	ExTwdLayMark,
	ExTwdLayMarkOpp,			// lay on other board
	
	ExDeltaBspSog,
	ExDeltaHdgCog,
	
	ExLayPortRatio,
	ExLayStrbRatio,
	
	ExFourierTwd,
	ExFourierTws,
	
	ExTargTwaP,
	ExTargBspP,

	ExNearestTide,
	
	ExPolCustom0,				// these need to be in this order : see CCore::DerivedPolarNumbers()
	ExPolCustom1,
	ExPolCustom2,
	ExPolCustom3,
	ExPolCustom0PC,
	ExPolCustom1PC,
	ExPolCustom2PC,
	ExPolCustom3PC,
	ExPolCustom0Targ,
	ExPolCustom1Targ,
	ExPolCustom2Targ,
	ExPolCustom3Targ,
	
	ExWaveSigHeight,			// XDR from Volvo wave sensor
	ExWaveSigPeriod,
	ExWaveMaxHeight,
	ExWaveMaxPeriod,
	
	ExSlam,
	ExHeave,
	
	ExMwa,
	ExMws,
	ExBoom,
	
	ExTargBspPercent,
	ExHeadingToSteer,
	ExHeadingToSteerPol,
	
	ExStartBspToPort,
	ExStartBspToStrb,
	ExStartBspOnPort,
	ExStartBspOnStrb,

	ExTwist,

	ExSailNow,
	ExSailMark,
	ExSailNext,

	ExTwdTwisted,

	ExTackLossVMGSec,
	ExTackLossVMGMetres,
	
	ExTripLog,
	ExDeltaMarkBrgCog,		// delta of cog and bearing to mark

	ExPitchRate,
	ExRollRate,

	ExDeltaPolBsp,
	ExDeltaTargRoll,

	ExDeflectorP,
	ExRudderP,
	ExRudderS,
	ExRudderToe,
	ExBspTransverse,
	ExForestayInner,
	ExGateTime,					// this is to the gate mark

	ExZeroAhead,
	ExBrgFromBoat0,
	ExRngFromBoat0,

	ExDeflectorS,
	ExBobstay,
	ExOuthaul,

	ExD0port,
	ExD0starboard,
	ExD1port,
	ExD1starbboard,
	ExV0port,
	ExV0starbboard,
	ExV1port,
	ExV1starbboard,

	ExStartTimeToPortSimple,
	ExStartTimeToStrbSimple,

	ExTargTwd,
	ExTargTwdDelta,
	ExPolarTws,
	ExPolarTwsDelta,
	ExPolarTwsPC,

	ExOppTrackCog,

	ExStartTimeToPortPinch,
	ExStartTimeToStrbPinch,

	ExPredTwd,
	ExPredTws,
	ExPredMSLP,

	ExNextMarkLat,
	ExNextMarkLon,

	ExBoomAngle,
	ExCunningham,
	ExForestayInnerHalyard,
	ExJibFurl,
	ExJibHalyard,

	ExMastCant,

	ExJ1,
	ExJ2,
	ExJ3,
	ExJ4,
	ExFoilP,
	ExFoilS,

	ExReacher,
	ExBlade,
	ExStaysail,
	ExSolent,
	ExTack,
	ExTackP,
	ExTackS,
	ExDeflectorUpper,
	ExDeflectorLower,
	ExWinchP,
	ExWinchS,
	ExSpinnakerP,
	ExSpinnakerS,
	ExMainHalyard,
	ExMast2,
		
	ExDeltaPolarRoll,

	ExLayPortBearMean,
	ExLayStrbBearMean,
	ExLayPortBearSD,
	ExLayStrbBearSD,

	ExStartTimeToPortBurn,
	ExStartTimeToStrbBurn,

	ExDepthAft,				// metres

	ExStartBurnPC,
	ExStartPolarBsp,
	ExStartGunBspTargPC,
	ExStartGunBspPolPC,
	ExStartLineTimeSP,

	ExDeltaCourseCog,
	ExLayTimeGPS,
		
	ExEngineTemp,
	ExEngineOilTemp,		//	ExEngineOilPressure is above
	ExTransmissionOilTemp,
	ExTransmissionOilPressure,
	ExFuelLevel,

	ExAmps,
	ExChargeState,

	ExGateRng,
	ExGateBrg,

//	ExLaK,
//	ExLoK,

//	ExSlam is spare above (note is logged var)

	ExNumChannels
};

// legacy/spare

//	ExHeave		??
//	ExWaveSigHeight,		// XDR from Volvo wave sensor
//	ExWaveSigPeriod,
//	ExWaveMaxHeight,
//	ExWaveMaxPeriod,